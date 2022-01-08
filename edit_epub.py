#import os
#import bs4
#import spacy
#import zipfile
#import shutil
#import russian_dictionary
#import argparse
import unicodedata
from russian_dictionary import RussianDictionary
from os import path, listdir, remove, rename, walk
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
parser.add_argument('-input_folder', type=str, help='for batch processing: the input folder')
parser.add_argument('-output_folder', type=str, help='for batch processing: the output folder')

args = parser.parse_args()
print(args.input)
print(args.output)

if args.input == None and args.input_folder == None:
    print("Please provide an input file!")
    quit()
elif args.input != None and args.input_folder != None:
    print("Please specify either an input file or an input folder!")
    quit()

FILE_NAME = args.input
OUTPUT_FILE = args.output

#FILE_NAME = "voina-i-mir.epub"
#OUTPUT_FILE = "voina-stressed.epub"

ANALYZE_GRAMMAR = True

extract_dir = "extract_dir_9580"
#with open("test.txt", "w") as f:
#    for a in sys.argv:
#        f.write(a)

def is_unimportant(token):
    return token.pos_ == "PUNCT" or token.pos_ == "SYM" or token.pos_ == "X" or token.pos_ == "SPACE" or token.text == "-"

def is_accented(phrase: str):
    for char in phrase:
        if char == u'\u0301':
            return True
    return False

ACCENT_MAPPING = {
        '́': '',
        '̀': '',
        'а́': 'а',
        'а̀': 'а',
        'е́': 'е',
        'ѐ': 'е',
        'и́': 'и',
        'ѝ': 'и',
        'о́': 'о',
        'о̀': 'о',
        'у́': 'у',
        'у̀': 'у',
        'ы́': 'ы',
        'ы̀': 'ы',
        'э́': 'э',
        'э̀': 'э',
        'ю́': 'ю',
        '̀ю': 'ю',
        'я́́': 'я',
        'я̀': 'я',
    }

ACCENT_MAPPING = {unicodedata.normalize('NFKC', i): j for i, j in ACCENT_MAPPING.items()}

def unaccentify( s):
    source = unicodedata.normalize('NFKC', s)
    for old, new in ACCENT_MAPPING.items():
        source = source.replace(old, new)
    return source

def remove_accent_if_only_one_syllable(s: str):
    s_unaccented = unaccentify(s)
    s_unaccented_lower = s_unaccented.lower()
    vowels = 0
    for char in s_unaccented_lower:
        if char in "аоэуыяеюи":
            vowels += 1
    if vowels <= 1:
        return s_unaccented
    else:
        return s

nlp = load("ru_core_news_sm")
if not ANALYZE_GRAMMAR:
    nlp.disable_pipes("tok2vec", "morphologizer", "parser", "attribute_ruler", "lemmatizer", "ner")

if not isfile("russian_dict.db"):
    print("Unpacking db...")
    with ZipFile("russian_dict.zip", "r") as dbfile:
        dbfile.extractall()

rd = RussianDictionary()

with ZipFile(FILE_NAME, "r") as zip_ref:
    zip_ref.extractall(extract_dir)

for subdir, dirs, files in walk("extract_dir_9580"):
    for file in files:
        filepath = path.join(subdir, file)
        if filepath.endswith(".xhtml"): 
            print(filepath)
            with open(filepath, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), "lxml")
                for text_object in soup.find_all(text=True):
                    text: str = text_object.text#.strip() - maybe commenting this out causes unnecessary calls of nlp
                    if len(text) > 0:
                        result_text = ""
                        doc = nlp(text)
                        skip_elements = 0
                        for i, token in enumerate(doc):
                            if skip_elements > 0:
                                skip_elements -= 1
                                continue
                            if is_unimportant(token):
                                result_text += token.text_with_ws
                            else:
                                if len(doc) >= i + 3 and doc[i + 1].text == "-" and token.whitespace_ == "" and doc[i + 1].whitespace_ == "":
                                    fusion_str = token.text + doc[i + 1].text + doc[i + 2].text
                                    fusion_str_stressed = rd.get_stressed_word_and_set_yo(fusion_str)
                                    if is_accented(fusion_str_stressed):
                                        #spl_str = fusion_str_stressed.split("-")
                                        #fusion_str_stressed = remove_accent_if_only_one_syllable(spl_str[0]) + "-" + remove_accent_if_only_one_syllable(spl_str[1])
                                        result_text += fusion_str_stressed + doc[i + 2].whitespace_
                                        #print(fusion_str_stressed)
                                        skip_elements = 2
                                        continue                              

                                if not ANALYZE_GRAMMAR:
                                    result_text += rd.get_stressed_word_and_set_yo(token.text) + token.whitespace_
                                else:
                                    str_wrd = rd.get_stressed_word_and_set_yo(token.text, token.pos_, token.morph)
                                    result_text += str_wrd + token.whitespace_

                        text_object.string.replace_with(result_text)

            with open(filepath, "w+", encoding="utf-8") as f:
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