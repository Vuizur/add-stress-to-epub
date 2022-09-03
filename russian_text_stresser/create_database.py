# 1. Create database using ebook-dictionary-creator (includes kaikki and OpenRussian)
# 2. Remove words that are incorrectly unstressed
# 3. Add data from Wikipedia to the database
# 4. Add data from Russian Wiktionary to the database, parse the Russian Wiktionary first

import os
from ebook_dictionary_creator.e_dictionary_creator.dictionary_creator import RussianDictionaryCreator
from ruwiktionary_htmldump_parser.htmldumpparser import HTMLDumpParser

from update_database import add_ruwiktionary_data_to_db, add_wikipedia_data_to_db, delete_unstressed_and_useless_words_from_DB
from wikipedia_dump_stress_extraction import extract_efficient

class DatabaseCreator:

    def __init__(self, htmldump_path):
        self.dictionary_creator = RussianDictionaryCreator()
        self.wiktionary_parser = HTMLDumpParser(htmldump_path)
    
    def create_database(self):
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
        print("Updating database with OpenRussian data")
        self.dictionary_creator.add_data_from_openrussian()
        print("Deleting unstressed words from database")
        delete_unstressed_and_useless_words_from_DB(self.dictionary_creator.database_path)

        if not os.path.exists(self.wiktionary_parser.intermediate_data_path):
            print("Parsing Russian Wiktionary HTML dump")
            self.wiktionary_parser.parse_wiktionary_dump()
        if not os.path.exists(self.wiktionary_parser.cleaned_data_path):
            print("Cleaning Russian Wiktionary data")
            self.wiktionary_parser.clean_entries()
        
        print("Adding Russian Wiktionary data to database")
        add_ruwiktionary_data_to_db(self.dictionary_creator.database_path, self.wiktionary_parser.cleaned_data_path)


        print("Extracting words from Russian Wikipedia")
        
        # TODO: Add data from Wikipedia to the database
        if not os.path.exists(wikipedia_stress_output_path):
            print("Creating wordlist from Russian Wikipedia")
            extract_efficient("STRESS", wikipedia_stress_output_path)
        
        print("Adding Russian Wikipedia data to database")
        add_wikipedia_data_to_db(self.dictionary_creator.database_path, wikipedia_stress_output_path)

        # Also add yo data from Wikipedia to the database
        # Also delete all data where there is only one possible option and add it to a pickled file or another sqlite table


if __name__ == "__main__":
    database_creator = DatabaseCreator( "D:/ruwiktionary")