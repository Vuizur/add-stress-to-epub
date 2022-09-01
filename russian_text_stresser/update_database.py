from dataclasses import dataclass
import json
import pickle
import sqlite3
from stressed_cyrillic_tools import get_lower_and_without_yo, unaccentify, is_unhelpfully_unstressed

@dataclass
class PossibleForms:
    unpronounced_word: dict

def find_words_that_only_have_one_meaning(cur: sqlite3.Cursor):
    """This output the words that do not require any context to be stressed correctly"""
    words = cur.execute(
        "SELECT canonical_form, alternative_canonical_form, word_lower_and_without_yo FROM word").fetchall()
                                            #unstressed_word, dict of compatible stressed versions
    unstressed_stressed_mapping: dict[str, list[str]] = {}
    definitely_ambiguous_words: set[str] = set()
    for canonical_form, alternative_canonical_form, word_lower_and_without_yo in words:
        if word_lower_and_without_yo in definitely_ambiguous_words:
            continue
        possible_stressed_forms: list[str] = [canonical_form]

        if alternative_canonical_form != None:
            possible_stressed_forms.append(alternative_canonical_form)

        if word_lower_and_without_yo not in unstressed_stressed_mapping:
            unstressed_stressed_mapping[word_lower_and_without_yo] = possible_stressed_forms
        else: #word is already_there
            already_existing_stressed_forms = unstressed_stressed_mapping[word_lower_and_without_yo]
            intersection = [x for x in possible_stressed_forms if x in already_existing_stressed_forms]
            if intersection == []:
                definitely_ambiguous_words.add(word_lower_and_without_yo)
                unstressed_stressed_mapping.pop(word_lower_and_without_yo)
            else:
                unstressed_stressed_mapping[word_lower_and_without_yo] = intersection
    for word, possible_forms in unstressed_stressed_mapping.items():
        if len(possible_forms) != 1:
            print(f"{word} - {possible_forms}")

    final_unstr_str_mapping = {k: v[0] for k, v in unstressed_stressed_mapping.items() if not k == v[0]}
    with open("simple_cases.pkl", "wb") as f:
        pickle.dump(final_unstr_str_mapping, f)
        #TODO: delete from DB


def delete_unstressed_and_useless_words_from_DB(dict_path: str = "russian_dict.db"):
    con = sqlite3.connect(dict_path)
    cur = con.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")
    cur.execute("SELECT word_id, canonical_form FROM word")
    words = cur.fetchall()
    for word_id, canonical_form in words:
        if is_unhelpfully_unstressed(canonical_form):
            cur.execute("DELETE FROM word WHERE word_id = ?", (word_id,))
    con.commit()

    con.execute("VACUUM;")
    cur.close()
    con.close()


def clean_unused_data_for_stress_lookup():
    con = sqlite3.connect("russian_dict.db")
    cur = con.cursor()
    find_words_that_only_have_one_meaning(cur)
    quit()
    # This is needed to get cascading delete
    cur.execute("PRAGMA foreign_keys = ON;")
    cur.execute("DROP table sense;")
    cur.execute("DROP table gloss;")
    cur.execute("ALTER TABLE word DROP COLUMN romanized_form;")
    cur.execute("ALTER TABLE word DROP COLUMN ipa_pronunciation;")
    cur.execute("ALTER TABLE word DROP COLUMN alternative_canonical_form;")
    cur.execute("ALTER TABLE form_of_word DROP COLUMN base_word_id")
    cur.execute("VACUUM;")
    con.commit()
    cur.close()
    con.close()




def add_word_to_db_if_not_there(canonical_form: str, cur: sqlite3.Cursor):
    """This is the simplest way to add stress data to the database."""
    # TODO: FINISH THIS
    word = unaccentify(canonical_form)
    word_lower = word.lower()
    lower_and_without_yo = get_lower_and_without_yo(canonical_form)
    cur.execute("SELECT * FROM word WHERE word_lower_and_without_yo = ?", (lower_and_without_yo,))
    
    if cur.fetchone() == None:
        #print(f"Inserted {canonical_form}")
        cur.execute("INSERT INTO word (canonical_form, word, word_lowercase, word_lower_and_without_yo) VALUES (?,?,?,?)", (canonical_form, word, word_lower, lower_and_without_yo))

def add_ruwiktionary_data_to_db(database_path = "russian_dict.db", ruwiktionary_json="ruwiktionary_words_fixed.json"):
    #TODO: Pay attention that some words have also two stress marks.
    con = sqlite3.connect(database_path)
    cur = con.cursor()
    # Load the list of dictionaries from the json file
    wordstress_word_mapping: dict[str, set[str]] = {}
    with open(ruwiktionary_json, "r", encoding="utf-8") as f:
        ruwiktionary_words = json.load(f)
        # Insert the data into the database
        for word in ruwiktionary_words:
            word_and_inflections: list[str] = [word["word"]] + word["inflections"]
            for wrd in word_and_inflections:
                wrd_unaccentified = get_lower_and_without_yo(wrd)
                # Add word to wordsstress_word_mapping, with an empty set as the value as default
                if wrd_unaccentified not in wordstress_word_mapping:
                    wordstress_word_mapping[wrd_unaccentified] = set()
                # Add the word to the list of words for this word
                wordstress_word_mapping[wrd_unaccentified].add(wrd.lower())
    for word, options in wordstress_word_mapping.items():
        if len(options) == 1:
            # The word only has one possible option to be accented correctly:
            # Add the word to the database
            add_word_to_db_if_not_there(options.pop(), cur)
        # TODO: Add the word to the database if it has two options
    con.commit()


if __name__ == "__main__":
    #update_database()
    #clean_unused_data_for_stress_lookup()
    #add_ruwiktionary_data_to_db()
    delete_unstressed_and_useless_words_from_DB()