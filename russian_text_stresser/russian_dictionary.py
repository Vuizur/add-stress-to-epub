from pathlib import Path
import pickle
import sqlite3
import re
from typing import Tuple
import os
import urllib.request
import zipfile
from stressed_cyrillic_tools import get_lower_and_without_yo


spacy_wiktionary_pos_mapping = {
    "NOUN": "noun",
    "VERB": "verb",
    "PROPN": "name",  # here it could also make sense to search nouns
    "ADV": "adv",
    "SCONJ": "conj",
    "ADP": "prep",  # not sure, fits for за
    "ADJ": "adj",
    "ADV": "adv",
    "PRON": "pron",
    "CCONJ": "conj",
    "PART": "particle",
    "DET": "pron",  # fits for какими
    "INTJ": "intj",
    "NUM": "num",
    "AUX": "verb",
    # Maybe num -> adv (больше)
}
spacy_wiktionary_number_mapping = {"Sing": "singular", "Plur": "plural"}
spacy_wiktionary_tense_mapping = {}
spacy_wiktionary_case_mapping = {
    "Nom": "nominative",
    "Gen": "genitive",
    "Dat": "dative",
    "Acc": "accusative",
    "Ins": "instrumental",
    "Loc": "prepositional",
    "Par": "partitive",
}

VERY_OFTEN_WRONG_WORDS = ["замер", "утра", "часа", "потом"]


class RussianDictionary:
    def __init__(self, db_file: str, simple_cases_file: str | None) -> None:
        russian_dict_path = Path(__file__).parent / db_file
        # If russian_dict.db doesn't exist, download it
        if not russian_dict_path.exists():
            print("Russian dictionary not found. Downloading...")
            self.download_data()

        if simple_cases_file is not None:
            simple_cases_path = Path(__file__).parent / simple_cases_file
            with open(simple_cases_path, "rb") as f:
                self.simple_cases: dict[str, str] = pickle.load(f)
        else:
            self.simple_cases = {}

        dict_path = russian_dict_path
        self._con = sqlite3.connect(dict_path)
        self._cur = self._con.cursor()

    def download_data(self):
        # Download the file from the URL https://github.com/Vuizur/add-stress-to-epub/releases/download/v1.0.1/russian_dict.zip

        url = "https://github.com/Vuizur/add-stress-to-epub/releases/download/v1.0.1/russian_dict.zip"
        file_name = Path(__file__).parent / "russian_dict.zip"
        russian_dict_path = Path(__file__).parent

        # Download the file
        urllib.request.urlretrieve(url, file_name)

        print("Download complete. Extracting...")
        # Unzip the file
        with zipfile.ZipFile(file_name, "r") as zip_ref:
            zip_ref.extractall(russian_dict_path)
        # Delete the zip file
        os.remove(file_name)
        print("Extraction complete.")

    @staticmethod
    def _replacenth(string, sub, wanted, n):
        where = [m.start() for m in re.finditer(sub, string)][n - 1]
        before = string[:where]
        after = string[where:]
        after = after.replace(sub, wanted, 1)
        return before + after

    @staticmethod
    def _turnyotoye(string):
        new_string = ""
        for char in string:
            if char == "ё":
                new_string += "е"
            else:
                new_string += char
        return new_string

    def get_dictionary_entry(self, word: str, e_try_index=-1):
        results = self._cur.execute(
            """SELECT g.gloss_string, s.sense_id, base_forms.word_id, COALESCE(base_forms.canonical_form, base_forms.word) AS canonical_word FROM gloss g INNER JOIN
sense AS s ON g.sense_id = s.sense_id 
INNER JOIN
(SELECT --This query gets all base forms, the direct ones and the ones over the relation table
    word_id, word, canonical_form
FROM
    (
    SELECT
        w.word_id AS word_id,
        w.word AS word,
        w.canonical_form AS canonical_form
    FROM
        word w
    WHERE
        w.word = ?
        AND NOT EXISTS
    (
        SELECT
            fow.base_word_id
        FROM
            form_of_word fow
        WHERE
            fow.word_id = w.word_id)
UNION
    SELECT
        base_w.word_id AS word_id,
        base_w.word AS word,
        base_w.canonical_form AS canonical_form
    FROM
        word base_w
    JOIN form_of_word fow 
ON
        base_w.word_id = fow.base_word_id
    JOIN word der_w 
ON
        der_w.word_id = fow.word_id
    WHERE
        der_w.word = ?)) base_forms ON s.word_id = base_forms.word_id""",
            (word, word),
        ).fetchall()

        if len(results) == 0:
            if word[0].isupper():
                return self.get_dictionary_entry(word.lower(), e_try_index)

            # this could contain unmarked ёs
            if word.count("е") > 0:
                if e_try_index == -1 and word.count("ё") == 0:
                    new_word_variation = self._replacenth(word, "е", "ё", 1)
                    return self.get_dictionary_entry(new_word_variation, e_try_index=1)
                elif e_try_index < word.count("ё") + word.count("е"):
                    eword = self._turnyotoye(word)
                    new_word_variation = self._replacenth(
                        eword, "е", "ё", e_try_index + 1
                    )
                    return self.get_dictionary_entry(
                        new_word_variation, e_try_index=e_try_index + 1
                    )

        res_dict = {}
        for gloss_string, sense_id, word_id, canonical_word in results:
            word_id = (canonical_word, word_id)
            if word_id not in res_dict:
                res_dict[word_id] = {}
            if sense_id not in res_dict[word_id]:
                res_dict[word_id][sense_id] = []
            res_dict[word_id][sense_id].append(gloss_string)

        fixed_res_dict = {}
        for k, v in res_dict.items():
            if k[0] not in fixed_res_dict:
                fixed_res_dict[k[0]] = []
            fixed_res_dict[k[0]] += list(v.values())

        # fixed_dict = {k[0]:list(v.values()) for (k,v) in res_dict.items()}

        return fixed_res_dict

    def write_word_with_yo(self, word: str, yo_dict_word: str):
        indices_of_yo = set()
        for i, char in enumerate(yo_dict_word):
            if char == "ё" or char == "Ё":
                indices_of_yo.add(i)
        wordlist = list(word)
        for i in indices_of_yo:
            if wordlist[i] == "Е":
                wordlist[i] = "Ё"
            else:
                wordlist[i] = "ё"
        return ("".join(wordlist), True)

    # Returns (result_word, bool: true if is_unique/not_in_database)
    def get_correct_yo_form(
        self, word: str, pos: str = None, morph=None
    ) -> Tuple[str, bool]:
        # is the word lowercased in the dictionary
        word_lower = word.lower()
        # TODO: Fix this and use GROUP BY

        words_with_possibly_written_yo = self._cur.execute(
            "SELECT w.word FROM word w WHERE w.word_lower_and_without_yo = ?",
            (word_lower,),
        ).fetchall()
        if words_with_possibly_written_yo == []:
            return (word, False)
        # elif len(set(words_with_possibly_written_yo)) == 1:
        #    return self.write_word_with_yo(word, words_with_possibly_written_yo[0])
        has_word_without_yo = False
        has_word_with_yo = False
        for wrd in words_with_possibly_written_yo:
            if "ё" in wrd[0]:
                has_word_with_yo = True
            else:
                has_word_without_yo = True
        if has_word_without_yo and has_word_with_yo:
            # try to find form according to morph
            if pos != None:
                pos = spacy_wiktionary_pos_mapping[pos]
                pos_filtered = self._cur.execute(
                    "SELECT w.word FROM word w WHERE w.word_lower_and_without_yo = ? AND w.pos = ? GROUP BY w.word",
                    (word_lower, pos),
                ).fetchall()
                # if len(pos_filtered) == 0 and pos == "name":
                #    pos_filtered = self._cur.execute("SELECT w.word FROM word w WHERE w.word_lower_and_without_yo = ? AND w.pos = \"noun\" GROUP BY w.word", (word_lower,)).fetchall()
                if len(pos_filtered) == 0:
                    print("Apparently wrong POS detected")
                    print(word)
                    print(pos)
                    return (word, False)
                elif len(pos_filtered) == 1:
                    return self.write_word_with_yo(word, pos_filtered[0][0])
                else:
                    tagged_results = self._cur.execute(
                        """
SELECT w.canonical_form, fow.form_of_word_id, tag_text
FROM word w 
JOIN form_of_word fow ON w.word_id = fow.word_id 
JOIN case_tags ct ON ct.form_of_word_id = fow.form_of_word_id
WHERE w.word_lower_and_without_yo = ? AND w.pos = ?
                    """,
                        (word_lower, pos),
                    ).fetchall()
                    morph_dict = morph.to_dict()
                    # fow, (word, form_tags)
                    fow_canonical_form_mapping: dict[int, str] = {}
                    grouped_forms: dict[int, set] = {}
                    for canonical_form, form_of_word_id, tag_text in tagged_results:
                        fow_canonical_form_mapping[form_of_word_id] = canonical_form
                        if form_of_word_id not in grouped_forms:
                            grouped_forms[form_of_word_id] = {tag_text}
                        else:
                            grouped_forms[form_of_word_id].add(tag_text)

                    if (
                        pos == "noun" or pos == "adj" or pos == "name" or pos == "pron"
                    ) and "Case" in morph_dict:
                        case = spacy_wiktionary_case_mapping[morph_dict["Case"]]
                        plurality = None
                        if "Number" in morph_dict:
                            plurality = spacy_wiktionary_number_mapping[
                                morph_dict["Number"]
                            ]
                        fitting_word_candidates = set()
                        for fow_key, tag_set in grouped_forms.items():
                            if case in tag_set and (
                                plurality in tag_set or plurality == None
                            ):
                                fitting_word_candidates.add(
                                    fow_canonical_form_mapping[fow_key]
                                )
                        if len(fitting_word_candidates) == 1:
                            return self.write_word_with_yo(
                                word, fitting_word_candidates.pop()
                            )
            return (word, False)
        elif has_word_without_yo == True:
            return (word, True)
        else:  # word must be written with a ё
            return self.write_word_with_yo(word, words_with_possibly_written_yo[0][0])

    @staticmethod
    def write_stressed_word(word: str, stressed_dict_word: str):
        index = 0
        result_word = ""
        for char in stressed_dict_word:
            # This is needed because some canonical words are incorrect in the database
            if char == "ё" or char == "Ё":
                yo_in_wrd = word[index]
                if yo_in_wrd == "е":
                    result_word += "ё"
                elif yo_in_wrd == "Е":
                    result_word += "Ё"
                index += 1
            elif char != "\u0301":
                if index >= len(word):
                    break
                result_word += word[index]
                index += 1
            else:
                result_word += "\u0301"
        return result_word

    # Returns the word unstressed if stress is unclear
    def get_stressed_word(self, word: str, pos=None, morph=None) -> str:
        if word.islower():
            is_lower = True
        else:
            is_lower = False
        word_lower = word.lower()
        words_in_dict = self._cur.execute(
            "SELECT canonical_form FROM word w WHERE w.word_lowercase = ?",
            (word_lower,),
        ).fetchall()
        canonical_list: set[str] = {
            wrd[0].lower()
            for wrd in words_in_dict
            if wrd[0] != None and not (is_lower and not wrd[0].islower())
        }
        if len(canonical_list) == 1:
            canonical_word = canonical_list.pop()
            return self.write_stressed_word(word, canonical_word)
        elif canonical_list == {None} or len(canonical_list) == 0 or pos == None:
            return word
        else:
            # Try to resolve ambiguities
            pos = spacy_wiktionary_pos_mapping[pos]
            pos_filtered = self._cur.execute(
                "SELECT w.canonical_form FROM word w WHERE w.word_lowercase = ? AND w.pos = ?",
                (word_lower, pos),
            ).fetchall()
            canonical_list: set[str] = {
                wrd[0].lower()
                for wrd in pos_filtered
                if wrd[0] != None and not (is_lower and not wrd[0].islower())
            }

            if len(canonical_list) == 0 and pos == "name":
                pos_filtered = self._cur.execute(
                    'SELECT w.word FROM word w WHERE w.word_lower_and_without_yo = ? AND w.pos = "noun" GROUP BY w.word',
                    (word_lower,),
                ).fetchall()
                canonical_list: set[str] = {
                    wrd[0].lower()
                    for wrd in pos_filtered
                    if wrd[0] != None and not (is_lower and not wrd[0].islower())
                }

            if len(canonical_list) == 0:
                print("Apparently wrong POS detected")
                print(word)
                print(pos)
                return word
            elif len(canonical_list) == 1:
                return self.write_stressed_word(word, canonical_list.pop())
            else:
                tagged_results = self._cur.execute(
                    """
SELECT w.canonical_form, fow.form_of_word_id, tag_text
FROM word w 
JOIN form_of_word fow ON w.word_id = fow.word_id 
JOIN case_tags ct ON ct.form_of_word_id = fow.form_of_word_id
WHERE w.word_lowercase = ? AND w.pos = ?
                """,
                    (word_lower, pos),
                ).fetchall()
                morph_dict = morph.to_dict()
                # fow, (word, form_tags)
                fow_canonical_form_mapping: dict[int, str] = {}
                grouped_forms: dict[int, set] = {}
                for canonical_form, form_of_word_id, tag_text in tagged_results:
                    fow_canonical_form_mapping[form_of_word_id] = canonical_form
                    if form_of_word_id not in grouped_forms:
                        grouped_forms[form_of_word_id] = {tag_text}
                    else:
                        grouped_forms[form_of_word_id].add(tag_text)
                if (
                    pos == "noun" or pos == "adj" or pos == "name" or pos == "pron"
                ) and "Case" in morph_dict:
                    case = spacy_wiktionary_case_mapping[morph_dict["Case"]]
                    plurality = None
                    if "Number" in morph_dict:
                        plurality = spacy_wiktionary_number_mapping[
                            morph_dict["Number"]
                        ]
                    fitting_word_candidates = set()
                    for fow_key, tag_set in grouped_forms.items():
                        if (
                            case in tag_set
                            and (plurality in tag_set or plurality == None)
                        ) or ("locative" in tag_set and morph_dict["Case"] == "Loc"):
                            fitting_word_candidates.add(
                                fow_canonical_form_mapping[fow_key]
                            )
                    if len(fitting_word_candidates) == 1:
                        return self.write_stressed_word(
                            word, fitting_word_candidates.pop()
                        )
                    else:
                        return word
                else:
                    return word

    def get_stressed_word_and_set_yo(self, word: str, pos=None, morph=None) -> str:
        if word.lower() in VERY_OFTEN_WRONG_WORDS:
            return word
        if pos == "PUNCT":
            return word

        # First look in simple_cases
        if get_lower_and_without_yo(word) in self.simple_cases:
            fitting_word = self.simple_cases[get_lower_and_without_yo(word)]
            return self.write_stressed_word(word, fitting_word)

        word_with_yo, is_unique = self.get_correct_yo_form(word, pos, morph)
        if not is_unique:
            return word
        else:
            return self.get_stressed_word(word_with_yo, pos, morph)
