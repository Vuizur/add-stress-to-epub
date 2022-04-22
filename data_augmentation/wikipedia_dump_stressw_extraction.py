from pathlib import Path
import re
import mwxml
from spacy import load
import time

def get_stressed_words_spacy(stressed_words: list, doc):
    for token in doc:
            tk_text = token.text
            if "\u0301" in tk_text:
                stressed_words.append(tk_text)
    return stressed_words

def get_stressed_words_regex(stressed_words: list,text: str):
    #This is needed because otherwise the string will not be split on backslashes
    #text = r"{}".format(text)
    #text = r"%s" % text
    # \xa0 is needed explicitly because its the backslash there is not interpreted as a backslash
    for word in re.split(r"'| |<|>|\[|\||\]|\n|\(|\)|»|«|:|\}|\\|=|\xa0", text):
        if "\u0301" in word:
            stressed_words.append(word)

def get_stressed_words_split(stressed_words: list, text: str):
    if text == None:
        return
    for temp_text in text.split(" "):
        if temp_text != None and "\u0301" in temp_text:
            for word in re.split(r"'| |<|>|\[|\||\]|\n|\(|\)|»|«|:|\}|\\|=|\xa0", temp_text):
                if "\u0301" in word:
                    stressed_words.append(word)
dump = mwxml.Dump.from_file(open("D:/ruwiki-20220401-pages-articles-multistream.xml", encoding= "utf-8"))

bundle_dir = Path(__file__).parent.parent.absolute()
nlp = load(bundle_dir / "ru_core_news_sm-3.1.0", exclude=["tok2vec", "morphologizer", "parser", "senter", "attribute_ruler", "lemmatizer", "ner"])

print(dump.site_info.name, dump.site_info.dbname)

stressed_words = []

k= 0
start = time.time()
for page in dump.pages:
    
    for revision in page:
        text: str = revision.text
        doc = nlp(text)
        #get_stressed_words_split(stressed_words, revision.text)
        get_stressed_words_spacy(stressed_words, doc)
        
    k+= 1


    
    if k > 10000:
        end = time.time()
        print(stressed_words)
        print(end - start)
        quit()
        
        #split_text = text.split("'''")
        #for i in range(1, len(split_text), 2):
        #    if "\u0301" in split_text[i]:
        #        stressed_words.append(split_text[i])    
#        space_split_tokens = text.split(" ")
#        for word in space_split_tokens:
#            if "\u0301" in word:
#                subwords_split_by_non_chars = re.split("'|<|>|[", word)
#                for subword in subwords_split_by_non_chars:
#                    if "\u0301" in subword:
#                        stressed_words.append(subword)
#    k += 1
#    if k > 1000:
#        print(stressed_words)
#        quit()
        