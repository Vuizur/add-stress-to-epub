import re
import mwxml
import time

from helper_methods import load_spacy_min
    # \xa0 is the no-break space

FINE_GRAINED_PATTERN = re.compile(
    r"'| |<|>|\[|\||\]|\n|\(|\)|»|«|:|\}|\{|\\|=|\xa0|’|‘|;|\.|,|\"|#|…|“|„|!|\?|_|%|&|[0-9]|\*|\+|@|‎|\/")


def get_stressed_words_spacy(stressed_words: list, doc):
    for token in doc:
        tk_text = token.text
        if "\u0301" in tk_text:
            stressed_words.append(tk_text)
    return stressed_words


def get_stressed_words_regex(stressed_words: list, text: str):
    # This is needed because otherwise the string will not be split on backslashes
    #text = r"{}".format(text)
    #text = r"%s" % text
    for word in re.split(r"'| |<|>|\[|\||\]|\n|\(|\)|»|«|:|\}|\\|=|\xa0", text):
        if "\u0301" in word:
            stressed_words.append(word)


def get_stressed_words_split(stressed_words: list, text: str):
    if text == None:
        return
    for temp_text in text.split(" "):
        if temp_text != None and "\u0301" in temp_text:
            # for word in re.split(r"'| |<|>|\[|\||\]|\n|\(|\)|»|«|:|\}|\\|=|\xa0|’|‘|;|.|,|\"", temp_text):
            for word in re.split(r"'| |<|>|\[|\||\]|\n|\(|\)|»|«|:|\}|\{|\\|=|\xa0|’|‘|;|\.|,|\"|#|…", temp_text):
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


def get_words_with_yo_with_stats(already_extracted_yo_set: set[str], yo_word_with_and_without_dict: dict, text: str):
    yo_dict: dict[str, tuple[int, int]] = {}
    # First number: with ё, second number: without ё

    if text == None:
        return
    for temp_text in text.split(" "):
        if temp_text != None and ("ё" in temp_text or "Ё" in temp_text or "е" in temp_text or "Е" in temp_text):
            for word in re.split(FINE_GRAINED_PATTERN, temp_text):
                if "ё" in word or "Ё" in word or "е" in word or "Е" in word:
                    yo_words.append(word)


# Not recommended, because it is very slow
def extract_spacy():
    dump = mwxml.Dump.from_file(
        open("D:/ruwiki-20220401-pages-articles-multistream.xml", encoding="utf-8"))

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


def extract_efficient():
    EXTRACTION_MODE = "YO"

    dump = mwxml.Dump.from_file(
        open("D:/ruwiki-20220401-pages-articles-multistream.xml", encoding="utf-8"))
    extracted_words = []
    k = 0
    start = time.time()
    for page in dump.pages:
        for revision in page:
            if EXTRACTION_MODE == "STRESS":
                get_stressed_words_split(extracted_words, revision.text)
            else:
                get_words_with_yo(extracted_words, revision.text)
        k += 1
        if k % 50000 == 0:
            print(k)
            end = time.time()
            # print(stressed_words)
            print(end - start)
    final_set = set(extracted_words)
    final_str = "\n".join(final_set)

    if EXTRACTION_MODE == "STRESS":
        filename = "D:/ruwiki_stress_wordlist.txt"
    else:
        filename = "D:/ruwiki_yo_wordlist.txt"

    with open(filename, "w", encoding="utf-8") as out:
        out.write(final_str)


if __name__ == "__main__":
    extract_efficient()
