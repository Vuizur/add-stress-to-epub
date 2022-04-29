from os import remove
from shutil import copy
import sqlite3
import subprocess


def update_database(clean_unused_data_for_stress_lookup=True):
    subprocess.run(["../wiktionary_extract_test/venv/Scripts/python.exe",
                   "../wiktionary_extract_test/update_russian_data.py"])
    try:
        remove("russian_dict.db")
    except:
        pass
    copy("../wiktionary_extract_test/russian_dict.db", "russian_dict.db")

    if clean_unused_data_for_stress_lookup:
        con = sqlite3.connect("russian_dict.db")
        cur = con.cursor()
        cur.execute("DROP table sense;")
        cur.execute("DROP table gloss;")
        cur.execute("VACUUM;")
        con.commit()
        cur.close()
        con.close()


if __name__ == "__main__":
    update_database()
