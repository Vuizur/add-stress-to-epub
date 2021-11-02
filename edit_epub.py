import os
import bs4
import spacy
import zipfile
import shutil
import russian_dictionary
import sys

FILE_NAME = "input.epub"
OUTPUT_FILE = "output.epub"

extract_dir = "extract_dir_9580"
#with open("test.txt", "w") as f:
#    for a in sys.argv:
#        f.write(a)

def is_unimportant(token):
    return token.pos_ == "PUNCT" or token.pos_ == "SYM" or token.pos_ == "X" or token.pos_ == "SPACE" or token.text == "-" or token.pos_ == "NUM"

rd = russian_dictionary.RussianDictionary()

nlp = spacy.load("ru_core_news_sm")
nlp.disable_pipes("tok2vec", "morphologizer", "parser", "attribute_ruler", "lemmatizer", "ner")

with zipfile.ZipFile(FILE_NAME, "r") as zip_ref:
    zip_ref.extractall(extract_dir)

for filename in os.listdir(extract_dir):
    if filename.endswith(".xhtml"): 
        print(filename)
        with open(os.path.join(extract_dir, filename), "r", encoding="utf-8") as f:
            soup = bs4.BeautifulSoup(f.read(), "lxml")
            for text_object in soup.find_all(text=True):
                text: str = text_object.text.strip()
                if len(text) > 0:
                    result_text = ""
                    doc = nlp(text)
                    for token in doc:
                        if is_unimportant(token):
                            result_text += token.text
                        else:
                            result_text += rd.get_stressed_word_and_set_yo(token.text) + token.whitespace_
                    text_object.string.replace_with(result_text)

        with open(os.path.join(extract_dir, filename), "w+", encoding="utf-8") as f:
            f.write(str(soup))
        continue
    else:
        continue


shutil.make_archive(OUTPUT_FILE, "zip", extract_dir)
try:
    os.remove(OUTPUT_FILE)
except:
    pass
os.rename(OUTPUT_FILE + ".zip", OUTPUT_FILE)
shutil.rmtree(extract_dir)