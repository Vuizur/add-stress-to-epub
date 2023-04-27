# 1. Create database using ebook-dictionary-creator (includes kaikki and OpenRussian)
# 2. Remove words that are incorrectly unstressed
# 3. Add data from Wikipedia to the database
# 4. Add data from Russian Wiktionary to the database, parse the Russian Wiktionary first

import os
import sqlite3
from ebook_dictionary_creator import RussianDictionaryCreator
from ruwiktionary_htmldump_parser import HTMLDumpParser

from russian_text_stresser.update_database import (
    add_ruwiktionary_data_to_db,
    add_wikipedia_data_to_db,
    clean_unused_data_for_stress_lookup,
    delete_unstressed_and_useless_words_from_DB,
    find_words_that_only_have_one_meaning,
)
from wikipedia_dump_stress_extraction import extract_efficient
import shutil


class DatabaseCreator:
    def __init__(self, htmldump_path):
        self.dictionary_creator = RussianDictionaryCreator()
        self.wiktionary_parser = HTMLDumpParser(htmldump_path)

    def create_database(self):
        TEMPORARY_DB_FOLDER = "D:/temporary_dictionary_dbs-new"
        if not os.path.exists(TEMPORARY_DB_FOLDER):
            os.mkdir(TEMPORARY_DB_FOLDER)

        kaikki_file_path = "russian-kaikki.json"
        wikipedia_stress_output_path = "wikipedia_words.txt"
        # If kaiiki file is not found, create it
        if not os.path.exists(kaikki_file_path):
            print("Downloading kaikki file")
            self.dictionary_creator.download_data_from_kaikki(kaikki_file_path)
        else:
            self.dictionary_creator.kaikki_file_path = kaikki_file_path
        print("Creating database")
        self.dictionary_creator.create_database()
        shutil.copy(
            self.dictionary_creator.database_path,
            TEMPORARY_DB_FOLDER + "/tempdb_0_enwiktionary_only.db",
        )

        print("Updating database with OpenRussian data")
        self.dictionary_creator.add_data_from_openrussian()
        print("Deleting unstressed/useless words from database")
        delete_unstressed_and_useless_words_from_DB(
            self.dictionary_creator.database_path
        )

        # Copy the database to a temporary folder
        if not os.path.exists(TEMPORARY_DB_FOLDER):
            os.mkdir(TEMPORARY_DB_FOLDER)
        shutil.copy(
            self.dictionary_creator.database_path,
            TEMPORARY_DB_FOLDER + "/tempdb_1_with_openrussian.db",
        )

        if not os.path.exists(self.wiktionary_parser.intermediate_data_path):
            print("Parsing Russian Wiktionary HTML dump")
            self.wiktionary_parser.parse_wiktionary_dump()
        if not os.path.exists(self.wiktionary_parser.cleaned_data_path):
            print("Cleaning Russian Wiktionary data")
            self.wiktionary_parser.clean_entries()

        print("Adding Russian Wiktionary data to database")
        add_ruwiktionary_data_to_db(
            self.dictionary_creator.database_path,
            self.wiktionary_parser.cleaned_data_path,
        )

        shutil.copy(
            self.dictionary_creator.database_path,
            TEMPORARY_DB_FOLDER + "/tempdb_2_with_ruwiktionary.db",
        )

        print("Extracting words from Russian Wikipedia")

        # TODO: Add data from Wikipedia to the database
        if not os.path.exists(wikipedia_stress_output_path):
            print("Creating wordlist from Russian Wikipedia")
            extract_efficient("STRESS", wikipedia_stress_output_path)

        print("Adding Russian Wikipedia data to database")
        add_wikipedia_data_to_db(
            self.dictionary_creator.database_path, wikipedia_stress_output_path
        )

        print("Deleting unstressed/useless words from database")
        delete_unstressed_and_useless_words_from_DB(
            self.dictionary_creator.database_path
        )

        shutil.copy(
            self.dictionary_creator.database_path,
            TEMPORARY_DB_FOLDER + "/tempdb_3_with_ruwikipedia.db",
        )
        print("Creating database with only necessary data")

        # Also add yo data from Wikipedia to the database
        # Also delete all data where there is only one possible option and add it to a pickled file or another sqlite table
        conn = sqlite3.connect(self.dictionary_creator.database_path)
        cur = conn.cursor()
        find_words_that_only_have_one_meaning(cur)

        cur.close()
        conn.close()
        print("Cleaning unused data")
        clean_unused_data_for_stress_lookup(self.dictionary_creator.database_path)
        delete_unstressed_and_useless_words_from_DB(
            self.dictionary_creator.database_path
        )
        shutil.copy(
            self.dictionary_creator.database_path,
            TEMPORARY_DB_FOLDER + "/tempdb_4_unnecessary_deleted.db",
        )


if __name__ == "__main__":
    database_creator = DatabaseCreator("D:/ruwiktionary-new")
    database_creator.create_database()
