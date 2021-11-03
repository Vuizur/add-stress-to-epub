#import os
#import bs4
#import spacy
#import zipfile
#import shutil
#import russian_dictionary
#import argparse
from russian_dictionary import RussianDictionary
from os import path, listdir, remove, rename
from os.path import isfile
from spacy import load
from argparse import ArgumentParser
from zipfile import ZipFile
from bs4 import BeautifulSoup
from shutil import make_archive, rmtree


parser = ArgumentParser(description='Add stress to Russian ebooks.')
parser.add_argument('-input', type=str,
                   help='the input file')
parser.add_argument('-output', type=str, help='the output file', default="output.epub")

args = parser.parse_args()
print(args.input)
print(args.output)

if args.input == None:
    print("Please provide an input file!")
    quit()

FILE_NAME = args.input
OUTPUT_FILE = args.output

extract_dir = "extract_dir_9580"
#with open("test.txt", "w") as f:
#    for a in sys.argv:
#        f.write(a)

def is_unimportant(token):
    return token.pos_ == "PUNCT" or token.pos_ == "SYM" or token.pos_ == "X" or token.pos_ == "SPACE" or token.text == "-" or token.pos_ == "NUM"

nlp = load("ru_core_news_sm")
nlp.disable_pipes("tok2vec", "morphologizer", "parser", "attribute_ruler", "lemmatizer", "ner")

if not isfile("words4.db"):
    print("Unpacking db...")
    with ZipFile("words4.zip", "r") as dbfile:
        dbfile.extractall()

rd = RussianDictionary()

with ZipFile(FILE_NAME, "r") as zip_ref:
    zip_ref.extractall(extract_dir)

for filename in listdir(extract_dir):
    if filename.endswith(".xhtml"): 
        print(filename)
        with open(path.join(extract_dir, filename), "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "lxml")
            for text_object in soup.find_all(text=True):
                text: str = text_object.text.strip()
                if len(text) > 0:
                    result_text = ""
                    doc = nlp(text)
                    for token in doc:
                        if is_unimportant(token):
                            result_text += token.text_with_ws
                        else:
                            #these get pronounced wrongly due to Spacy's tokenization
                            if token.text == "моему" or token.text == "твоему":
                                result_text += token.text_with_ws
                            else:
                                result_text += rd.get_stressed_word_and_set_yo(token.text) + token.whitespace_
                    text_object.string.replace_with(result_text)

        with open(path.join(extract_dir, filename), "w+", encoding="utf-8") as f:
            f.write(str(soup))
        continue
    else:
        continue


make_archive(OUTPUT_FILE, "zip", extract_dir)
try:
    remove(OUTPUT_FILE)
except:
    pass
rename(OUTPUT_FILE + ".zip", OUTPUT_FILE)
rmtree(extract_dir)