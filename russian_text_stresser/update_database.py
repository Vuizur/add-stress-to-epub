from dataclasses import dataclass
from os import remove
import pickle
from shutil import copy
import sqlite3
import subprocess

@dataclass
class PossibleForms:
    unpronounced_word: dict

def find_words_that_only_have_one_meaning(cur: sqlite3.Cursor):
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

    final_unstr_str_mapping = {k: v[0] for k, v in unstressed_stressed_mapping.items()}
    with open("simple_cases.pkl", "wb") as f:
        pickle.dump(final_unstr_str_mapping, f)
        #TODO: delete from DB




def clean_unused_data_for_stress_lookup():
    con = sqlite3.connect("russian_text_stresser/russian_dict.db")
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


def update_database(clean_unused_data=True):
    subprocess.run(["../wiktionary_extract_test/venv/Scripts/python.exe",
                   "../wiktionary_extract_test/update_russian_data.py"])
    try:
        remove("russian_dict.db")
    except:
        pass
    copy("../wiktionary_extract_test/russian_dict.db", "russian_dict.db")

    if clean_unused_data:
        clean_unused_data_for_stress_lookup()


if __name__ == "__main__":
    #update_database()
    clean_unused_data_for_stress_lookup()