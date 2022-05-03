from distutils.command import clean
from os import remove
from shutil import copy
import sqlite3
import subprocess

def clean_unused_data_for_stress_lookup():
    con = sqlite3.connect("russian_dict.db")
    cur = con.cursor()
    cur.execute("PRAGMA foreign_keys = ON;") # This is needed to get cascading delete
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
    update_database()
