import os
import re
import sqlite3
import mwxml
import time
from stressed_cyrillic_tools import remove_yo

from helper_methods import load_spacy_min
from spacy.tokens import Doc

# \xa0 is the no-break space

FINE_GRAINED_PATTERN = re.compile(
    r"'| |<|>|\[|\||\]|\n|\(|\)|»|«|:|\}|\{|\\|=|\xa0|’|‘|;|\.|,|\"|#|…|“|„|!|\?|_|%|&|[0-9]|\*|\+|@|‎|\/"
)


def get_stressed_words_spacy(stressed_words: list[str], doc: Doc):
    for token in doc:
        tk_text = token.text
        if "\u0301" in tk_text:
            stressed_words.append(tk_text)
    return stressed_words


def get_stressed_words_regex(stressed_words: list[str], text: str):
    # This is needed because otherwise the string will not be split on backslashes
    # text = r"{}".format(text)
    # text = r"%s" % text
    for word in re.split(r"'| |<|>|\[|\||\]|\n|\(|\)|»|«|:|\}|\\|=|\xa0", text):
        if "\u0301" in word:
            stressed_words.append(word)


def get_stressed_words_split(stressed_words: list[str], text: str):
    if text == None:
        return
    for temp_text in text.split(" "):
        if temp_text != None and "\u0301" in temp_text:
            # for word in re.split(r"'| |<|>|\[|\||\]|\n|\(|\)|»|«|:|\}|\\|=|\xa0|’|‘|;|.|,|\"", temp_text):
            # for word in re.split(r"'| |<|>|\[|\||\]|\n|\(|\)|»|«|:|\}|\{|\\|=|\xa0|’|‘|;|\.|,|\"|#|…", temp_text):
            for word in re.split(FINE_GRAINED_PATTERN, temp_text):
                if "\u0301" in word:
                    stressed_words.append(word)


def get_words_with_yo(yo_words: list, text: str):
    if text == None:
        return
    for temp_text in text.split(" "):
        if temp_text != None and "ё" in temp_text or "Ё" in temp_text:
            # for word in re.split(r"'| |<|>|\[|\||\]|\n|\(|\)|»|«|:|\}|\\|=|\xa0|’|‘|;|.|,|\"", temp_text):
            # for word in re.split(r"'| |<|>|\[|\||\]|\n|\(|\)|»|«|:|\}|\{|\\|=|\xa0|’|‘|;|\.|,|\"|#|…|“|„|!|\?|_|%|&|[0-9]|\*|\+|@|‎|\/", temp_text):
            for word in re.split(FINE_GRAINED_PATTERN, temp_text):
                if "ё" in word or "Ё" in word:
                    yo_words.append(word)


def get_words_with_yo_with_stats(yo_database_cursor: sqlite3.Cursor, text: str):
    if text == None:
        return
    for temp_text in text.split(" "):
        if temp_text != None and (
            "ё" in temp_text or "Ё" in temp_text or "е" in temp_text or "Е" in temp_text
        ):
            for word in re.split(FINE_GRAINED_PATTERN, temp_text):
                if "ё" in word or "Ё" in word:
                    # Increment the with_yo count in the database
                    yo_database_cursor.execute(
                        "UPDATE yo_stats SET yo_count = yo_count + 1 WHERE with_yo = ?",
                        (word,),
                    )
                elif "е" in word or "Е" in word:
                    # Increment the without_yo count in the database
                    yo_database_cursor.execute(
                        "UPDATE yo_stats SET without_yo_count = without_yo_count + 1 WHERE without_yo = ?",
                        (word,),
                    )


# Not recommended, because it is very slow
def extract_spacy():
    dump = mwxml.Dump.from_file(
        open("D:/ruwiki-20220401-pages-articles-multistream.xml", encoding="utf-8")
    )

    nlp = load_spacy_min
    start = time.time()
    stressed_words = []
    print(dump.site_info.name, dump.site_info.dbname)
    for page in dump.pages:
        for revision in page:
            doc = nlp(revision.text)
            get_stressed_words_spacy(stressed_words, doc)

        k += 1
        if k % 50000 == 0:
            print(k)
            end = time.time()

            print(end - start)
    final_set = set(stressed_words)
    final_str = "\n".join(final_set)
    with open("D:/ruwiki_wordlist.txt", "w", encoding="utf-8") as out:
        out.write(final_str)


CREATE_YO_STATS_SQL = """
CREATE TABLE IF NOT EXISTS yo_stats (
    with_yo TEXT NOT NULL,
    without_yo TEXT NOT NULL,
    yo_count INTEGER NOT NULL,
    without_yo_count INTEGER NOT NULL,
    yo_percent REAL,
    PRIMARY KEY (with_yo, without_yo)
);
"""
SET_YO_STATS_INDICES_SQL = """
CREATE INDEX IF NOT EXISTS yo_stats_with_yo_index ON yo_stats (with_yo);
CREATE INDEX IF NOT EXISTS yo_stats_without_yo_index ON yo_stats (without_yo);
"""


def extract_efficient(
    extraction_mode: str = "STRESS", wordlist_path: str = "ruwiki_wordlist.txt", DUMP_PATH: str = "D:/ruwiki-20220820-pages-articles-multistream.xml"
):
    """The extraction mode can be either "STRESS" or "YO\" """
    # EXTRACTION_MODE = "YO"

    

    dump = mwxml.Dump.from_file(open(DUMP_PATH, encoding="utf-8"))
    extracted_words: list[str] = []
    k = 0
    start = time.time()
    for page in dump.pages:
        for revision in page:
            if extraction_mode == "STRESS":
                get_stressed_words_split(extracted_words, revision.text)
            else:
                get_words_with_yo(extracted_words, revision.text)
        k += 1
        if k % 50000 == 0:
            print(k)
            end = time.time()

            print(end - start)

    if extraction_mode == "YO":
        extracted_words_set = set(extracted_words)
        print("Gathering more detailed yo statistics")
        DATABASE_PATH = "ruwiki_yo_stats.db"
        # Delete the database if it already exists
        if os.path.exists(DATABASE_PATH):
            os.remove(DATABASE_PATH)

        # Create yo stats table
        with sqlite3.connect(DATABASE_PATH) as conn:
            cur = conn.cursor()
            cur.execute(CREATE_YO_STATS_SQL)
            for word in extracted_words_set:
                # Insert into yo stats table
                cur.execute(
                    "INSERT INTO yo_stats (with_yo, without_yo, yo_count, without_yo_count, yo_percent) VALUES (?, ?, ?, ?, ?);",
                    (word, remove_yo(word), 0, 0, 0),
                )
            # Create indices
            cur.executescript(SET_YO_STATS_INDICES_SQL)
            k = 0

            # Reset dump.pages generator
            dump = mwxml.Dump.from_file(open(DUMP_PATH, encoding="utf-8"))

            for page in dump.pages:
                for revision in page:
                    get_words_with_yo_with_stats(cur, revision.text)
                k += 1
                if k % 50000 == 0:
                    print(k)

            # Update yo_percent, use real division
            cur.execute(
                "UPDATE yo_stats SET yo_percent = 100 * CAST(yo_count AS REAL) / (yo_count + without_yo_count)"
            )

            # Commit
            conn.commit()

    final_set = set(extracted_words)
    final_str = "\n".join(final_set)

    with open(wordlist_path, "w", encoding="utf-8") as out:
        out.write(final_str)


if __name__ == "__main__":
    extract_efficient("YO", "ruwiki_yo_wordlist.txt")
