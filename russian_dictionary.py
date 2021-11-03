import sqlite3
import re
from typing import Tuple

class RussianDictionary:
    _con = sqlite3.connect("words4.db")
    _cur = _con.cursor()

    @staticmethod
    def _replacenth(string, sub, wanted, n):
        where = [m.start() for m in re.finditer(sub, string)][n-1]
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

    def get_dictionary_entry(self, word: str, e_try_index = -1):
        results = self._cur.execute("""SELECT g.gloss_string, s.sense_id, base_forms.word_id, COALESCE(base_forms.canonical_form, base_forms.word) AS canonical_word FROM gloss g INNER JOIN
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
        der_w.word = ?)) base_forms ON s.word_id = base_forms.word_id""", (word, word)).fetchall()

        if len(results) == 0:
            if word[0].isupper():
                return self.get_dictionary_entry(word.lower(), e_try_index)

            #this could contain unmarked ёs
            if word.count("е") > 0:
                if  e_try_index == -1 and word.count("ё") == 0: 
                    new_word_variation = self._replacenth(word, "е", "ё", 1)
                    return self.get_dictionary_entry(new_word_variation, e_try_index = 1)
                elif e_try_index < word.count("ё") + word.count("е"):
                    eword = self._turnyotoye(word)
                    new_word_variation = self._replacenth(eword, "е", "ё", e_try_index + 1)
                    return self.get_dictionary_entry(new_word_variation, e_try_index= e_try_index + 1)


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

        #fixed_dict = {k[0]:list(v.values()) for (k,v) in res_dict.items()}
            
        return fixed_res_dict
    #Returns (result_word, bool: true if is_unique/not_in_database) 
    def get_correct_yo_form(self, word: str) -> Tuple[str, bool]:
        
        #is the word lowercased in the dictionary
        word_lower = word.lower()
        #word_in_dict = self._cur.execute("SELECT * FROM word w WHERE w.word_lowercase = ?",(word_lower,)).fetchone()
        #TODO: Fix all of this, I am too tired
        #if word_in_dict != None:
        #    return word
        #else:
        words_with_possibly_written_yo = self._cur.execute("SELECT w.word FROM word w WHERE w.word_lower_and_without_yo = ?", 
            (word_lower,)).fetchall()
        if words_with_possibly_written_yo == []:
            return (word, False)
        else:
            has_word_without_yo = False
            has_word_with_yo = False
            for wrd in words_with_possibly_written_yo:
                if "ё" in wrd[0]:
                    has_word_with_yo = True
                else:
                    has_word_without_yo = True
            if has_word_without_yo and has_word_with_yo:
                return(word, False)
            elif has_word_without_yo == True:
                return(word, True)
            else: #word must be written with a ё
                indices_of_yo = set()
                for i, char in enumerate(words_with_possibly_written_yo[0][0]):
                    if char == "ё" or char == "Ё":
                        indices_of_yo.add(i)
                wordlist = list(word)
                for i in indices_of_yo:
                    if wordlist[i] == "Е":
                        wordlist[i] = "Ё"
                    else:
                        wordlist[i] = "ё"
                return ("".join(wordlist), True)

    #Returns the word unstressed if stress is unclear
    def get_stressed_word(self, word: str) -> str:
        if word.islower():
            is_lower = True
        else:
            is_lower = False
        word_lower = word.lower()
        words_in_dict = self._cur.execute("SELECT canonical_form FROM word w WHERE w.word_lowercase = ?",(word_lower,)).fetchall()
        canonical_list: set[str] = {wrd[0] for wrd in words_in_dict if wrd[0] != None and not (is_lower and not wrd[0].islower())}
        if len(canonical_list) > 1 or canonical_list == {None} or len(canonical_list) == 0:
            return word

        canonical_word = canonical_list.pop()
        index = 0
        result_word = ""
        for char in canonical_word:
            #This is needed because some canonical words are incorrect in the database
            if char != u'\u0301':
                if index >= len(word):
                    break
                result_word += word[index]
                index += 1
            else:
                result_word += u'\u0301'
            
        return result_word
    
    def get_stressed_word_and_set_yo(self, word: str) -> str:
        word_with_yo, is_unique = self.get_correct_yo_form(word)
        if not is_unique:
            return word
        else:
            return self.get_stressed_word(word_with_yo)