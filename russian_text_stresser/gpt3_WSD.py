from collections import namedtuple
from dataclasses import dataclass
import os
from typing import Optional, TypedDict
import openai
import sqlite3
import json
from stressed_cyrillic_tools import (
    unaccentify,
    remove_yo,
    has_acute_accent_or_only_one_syllable,
)
from ruwiktionary_htmldump_parser import HTMLDumpParser
from helper_methods import load_spacy_min

from russian_dictionary import RussianDictionary

# JSON has format like this
# {
#    "word": "весы́",
#    "inflections": [
#      "весо́в",
#      "веса́ми",
#      "веса́х",
#      "веса́м"
#    ],
#    "definitions": [
#      "прибор для измерения массы"
#    ],
#    "grammar_info": "Существительное, неодушевлённое, мужской род, 2-е склонение (тип склонения мн. <м 1b>  по классификации А. А. Зализняка); формы ед. ч. не используются.",
#    "IPA": "vʲɪˈsɨ"
# },

# Entry = TypedDict(
#    "Entry",
#    {
#        "word": str,
#        "alternative_form": Optional[str],
#        "inflections": list[str],
#        "definitions": list[str],
#        "grammar_info": str,
#        "IPA": str,
#    },
# )
@dataclass
class Entry:
    word: str
    alternative_form: Optional[str]
    inflections: list[str]
    definitions: list[str]
    grammar_info: str
    IPA: str


# Entries = TypedDict(
#    "Entries",
#    {
#        "word": Entry,
#    },
# )


class RuWiktionary:
    def __init__(
        self, russian_wiktionary_json_path: str, database_path: str = "ruwiktionary.db"
    ):
        # Read the JSON file into aSQLIte database with a table for the words, and a separate table for the inflections
        # We use an database because this will be much faster than scanning the JSON file every time
        if not os.path.isfile(database_path):
            self.conn = sqlite3.connect(database_path)
            self.cursor = self.conn.cursor()

            self.cursor.execute(
                "CREATE TABLE words (word_id INTEGER PRIMARY KEY, word TEXT, word_lower_unstressed TEXT, definitions TEXT, grammar_info TEXT, IPA TEXT)"
            )
            self.cursor.execute(
                "CREATE TABLE inflections (inflection_id INTEGER PRIMARY KEY, word_id INTEGER, inflection TEXT, inflection_lower_unstressed TEXT, FOREIGN KEY(word_id) REFERENCES words(word_id))"
            )
            with open(russian_wiktionary_json_path, "r", encoding="utf-8") as f:
                all_words = json.load(f)
                for word in all_words:
                    self.cursor.execute(
                        "INSERT INTO words (word, word_lower_unstressed, definitions, grammar_info, IPA) VALUES (?, ?, ?, ?, ?)",
                        (
                            word["word"],
                            remove_yo(unaccentify(word["word"].lower())),
                            json.dumps(word["definitions"], ensure_ascii=False),
                            word["grammar_info"],
                            word["IPA"],
                        ),
                    )
                    word_id = self.cursor.lastrowid
                    for inflection in word["inflections"]:
                        self.cursor.execute(
                            "INSERT INTO inflections (word_id, inflection, inflection_lower_unstressed) VALUES (?, ?, ?)",
                            (
                                word_id,
                                inflection,
                                remove_yo(unaccentify(inflection.lower())),
                            ),
                        )

            # Add index to unstressed columns
            self.cursor.execute(
                "CREATE INDEX words_lower_unstressed_index ON words (word_lower_unstressed)"
            )
            self.cursor.execute(
                "CREATE INDEX inflections_lower_unstressed_index ON inflections (inflection_lower_unstressed)"
            )
            self.cursor.execute(
                "CREATE INDEX inflections_idx_0435a8e8 ON inflections(word_id)"
            )

            self.cursor.execute("CREATE INDEX words_idx_0435a8e8 ON words(word_id)")

            self.cursor.execute(
                """CREATE VIEW words_with_inflections AS SELECT words.word_id, words.word, words.definitions, words.grammar_info, words.IPA, GROUP_CONCAT(inflections.inflection, "|") AS inflections FROM words LEFT JOIN inflections ON words.word_id = inflections.word_id GROUP BY words.word_id"""
            )

            self.conn.commit()
        else:
            self.conn = sqlite3.connect(database_path)
            self.cursor = self.conn.cursor()

    def get_entries(self, word: str) -> list[Entry]:
        """Searches for all fitting entries for an (unstressed) word in the database and returns the words and its inflections"""
        self.cursor.execute(
            "SELECT word_id, word, definitions, grammar_info, IPA FROM words WHERE word_lower_unstressed = ?",
            (remove_yo(unaccentify(word.lower())),),
        )
        rows = self.cursor.fetchall()

        inflection_word_ids = self.get_entries_with_inflection(word)
        if inflection_word_ids is not None:
            for word_id in inflection_word_ids:
                # Check if we already have this word_id
                if not any(word_id == row[0] for row in rows):
                    self.cursor.execute(
                        "SELECT word_id, word, definitions, grammar_info, IPA FROM words WHERE word_id = ?",
                        (word_id,),
                    )
                    rows.append(self.cursor.fetchone())

        if len(rows) == 0:
            return None
        else:
            return [
                # {
                #    "word": row[1],
                #    "definitions": json.loads(row[2]),
                #    "grammar_info": row[3],
                #    "IPA": row[4],
                #    "inflections": self.get_inflections(row[0]),
                # }
                Entry(
                    word=row[1],
                    alternative_form=None,
                    definitions=json.loads(row[2]),
                    grammar_info=row[3],
                    IPA=row[4],
                    inflections=self.get_inflections(row[0]),
                )
                for row in rows
            ]

    def get_inflections(self, word_id: int) -> list:
        """Returns a list of inflections for a given word_id"""
        self.cursor.execute(
            "SELECT inflection FROM inflections WHERE word_id = ?", (word_id,)
        )
        return [row[0] for row in self.cursor.fetchall()]

    def get_entries_with_inflection(self, word: str) -> list[int]:
        """Returns all fitting entries where the word is an inflection of the base word"""
        self.cursor.execute(
            "SELECT words.word_id FROM words INNER JOIN inflections ON words.word_id = inflections.word_id WHERE inflection_lower_unstressed = ?",
            (remove_yo(unaccentify(word.lower())),),
        )
        rows = self.cursor.fetchall()
        if len(rows) == 0:
            return None
        else:
            return [row[0] for row in rows]

    def get_words_with_only_one_choice(self) -> list[str]:
        """Returns a list of words with only one choice in the database"""

        # named dict that contains (word_lower_unstressed, list of stress options)
        stress_options = defaultdict(list)
        StressOptions = named(
            "StressOptions", ["word_lower_unstressed", "stress_options"]
        )

    def __del__(self):
        self.conn.close()


class WordSenseDisambiguator:
    def __init__(
        self, russian_wiktionary_json_path: str = "ruwiktdata_cleaned.json"
    ) -> None:
        # If openai-key.txt is not found, message the user to create it
        if not os.path.exists("openai-key.txt"):
            raise FileNotFoundError(
                "Please create openai-key.txt and put your OpenAI API key in it"
            )
        with open("openai-key.txt", "r", encoding="utf-8") as f:
            openai.api_key = f.readline().strip()
        self.russian_wiktionary = RuWiktionary(russian_wiktionary_json_path)

    @staticmethod
    def find_in_entry_matching_word(word: str, entry: Entry) -> list[str]:
        """Returns all matching words in an entry that could be the word"""
        # Return the word and all inflections that match the word in their unstressed form
        # assert entry["inflections"] is not None
        assert entry.inflections is not None
        compatible_words = [
            inflection.lower()
            # for inflection in entry["inflections"] + [entry["word"]]
            for inflection in entry.inflections + [entry.word]
            if remove_yo(unaccentify(inflection.lower()))
            == remove_yo(unaccentify(word.lower())) and not (inflection[0].isupper and word[0].islower())
        ]
        return compatible_words

    @staticmethod
    def find_in_entries_matching_words(word: str, entries: list[Entry]) -> list[str]:
        """Returns all matching words in all entries that are compatible with the word"""
        compatible_words = set()
        for entry in entries:
            compatible_words.update(
                WordSenseDisambiguator.find_in_entry_matching_word(word, entry)
            )
        return list(compatible_words)

    def exists_in_wiktionary(self, word: str) -> bool:
        """Returns whether the word exists in the wiktionary"""
        return self.russian_wiktionary.get_entries(word) is not None

    def only_one_choice_exists(self, word: str, entries: list[Entry]) -> bool:
        """Returns whether there is only one choice for a given word"""
        return len(self.find_in_entries_matching_words(word, entries)) == 1

    def is_impossible_to_disambiguate(self, word: str, entries: list[Entry]) -> bool:
        """Returns whether one of the entries has at least 2 options -> impossible to disambiguate using our data
        even after disambiguation"""
        return any(
            len(self.find_in_entry_matching_word(word, entry)) > 1 for entry in entries
        )

    def disambiguate(self, word: str, context: str, word_index: int = 1) -> None | str:
        """Returns the correctly stressed word"""
        valid_entries = self.russian_wiktionary.get_entries(word)
        if valid_entries is None or len(valid_entries) == 0:
            return None
        elif self.only_one_choice_exists(word, valid_entries):
            return RussianDictionary.write_stressed_word(
                word, self.find_in_entries_matching_words(word, valid_entries)[0]
            )
        elif self.is_impossible_to_disambiguate(word, valid_entries):
            return None
        else:
            # for entry in valid_entries:
            #    matching_words = self.find_in_entry_matching_word(word, entry)
            #    assert (
            #        matching_words != []
            #    ), "No matching words found, this should not happen"
            #
            #    # Generate all the options
            options = "\n".join(
                [
                    f"{i + 1}. {entry.word} ({entry.grammar_info.replace(',', ' ').replace(';', ' ').split(' ')[0]}) - {entry.definitions[0].split('◆')[0].strip()}"
                    for i, entry in enumerate(valid_entries)
                ]
            )

            question = f"""
Фраза: "{context}"
Вопрос: Какое определение слова "{word}" здесь правильное?
{options}
Ответ:"""
            print(question)

    def detect_and_fix_missing_stressed_words(self, text: str) -> str:
        """Uses GPT3-based word sense disambiguation to try to fix missing stressed words"""
        nlp = load_spacy_min()
        nlp.add_pipe("sentencizer")
        doc = nlp(text)
        # Iterate over sentences
        for sent in doc.sents:
            # Iterate over words
            for word in sent:
                if has_acute_accent_or_only_one_syllable(word.text):
                    continue
                # If the word is not stressed, try to fix it
                self.disambiguate(word.text, sent.text)


if __name__ == "__main__":
    # hd = HTMLDumpParser(None, "ruwiktdata_int.json", "ruwiktdata_cleaned.json")
    # hd.clean_entries()
    # quit()
    # rw = RuWiktionary("ruwiktdata_cleaned.json")
    ##word = "леса"
    # word = "лица"
    # word = "замок"
    # entries = rw.get_entries(word)
    # print("Number of entries:", len(entries))
    # print(entries)
    # wsd = WordSenseDisambiguator()
    # matchwords = wsd.find_in_entries_matching_words(word, entries)
    # print(f"Is impossible to disambiguate: {wsd.is_impossible_to_disambiguate(word, entries)}")
    # print(matchwords)

    wsd = WordSenseDisambiguator()
    print(wsd.disambiguate("замок", "В замке было очень темно."))
    print(
        wsd.disambiguate(
            "потом",
            "С потом переносятся феромоны и множество биологически активных веществ.",
        )
    )

    # Load disambiguation_text.txt
    with open("disambiguation_text.txt", "r", encoding="utf-8") as f:
        text = f.read()
    wsd.detect_and_fix_missing_stressed_words(text)

    # wsd.detect_and_fix_missing_stressed_words("В замке было очень темно.")
