from distutils.command.build_scripts import first_line_re
import os
from pathlib import Path
import json
from bs4 import BeautifulSoup, PageElement
import re
# has to contain cyrillic, but not the characters only other slavic languages have


def can_be_russian(text: str):
    text_lower = text.lower()
    return bool(re.search('[а-яА-Я]', text)) and "ў" not in text_lower and "ї" not in text_lower and "є" not in text_lower and \
        "ћ" not in text_lower and "ђ" not in text_lower and "ґ" not in text_lower and "і" not in text_lower


def get_lemma(lemma_bold_paragraph) -> str:
    if lemma_bold_paragraph.find("span"):
        for span in lemma_bold_paragraph.find_all("span"):
            span.extract()
        return lemma_bold_paragraph.text
    else:
        return lemma_bold_paragraph.text


def get_morph_table_words(morph_table) -> list[str]:
    words: list[str] = []
    rows = morph_table.find("tbody").find_all("tr")
    for row in rows:
        cells = row.find_all("td")
        for cell in cells[1:]:  # Leave out left definition cell

            words.extend(cell.get_text("|").split("|"))

    return [word for word in words if word != "-" and word != "—"]


def extract_stressed_words_from_section(section: PageElement) -> tuple[str, list[str]]:
    lemma_p = section.find("p")
    lemma = get_lemma(lemma_p.b)

    morpher_table = section.find("table", {"class": "morfotable"})
    if morpher_table != None:
        morph_table_words = get_morph_table_words(morpher_table)
        # print(morph_table_words)
        return (lemma, morph_table_words)
    else:
        return (lemma, None)


def get_stressed_words_from_html(html: str) -> dict[str, list[str]]:
    # print(html)
    # lxml is supposed to be the fastest parser
    #lemma: str = None

    soup = BeautifulSoup(html, "lxml")
    # The HTML dump pages are structured differently from the online hosted version
    inflection_dict = {}
    russian_h1 = soup.find("h1", id="Русский")
    if russian_h1 != None:
        for sibling in russian_h1.next_siblings:
            if sibling.name == "section":
                section_res = extract_stressed_words_from_section(sibling)
                if section_res == None:
                    return None
                else:
                    lemma, inflections = section_res
                    inflection_dict[lemma] = inflections
                    return inflection_dict
                
    else:
        return None


def extract_words_from_html_dump():
    word_dict: dict[str, list[str]] = {}
    word_set = set()
    i = 0
    for path in os.scandir("D:/ruwiktionary-NS0-20220501-ENTERPRISE-HTML.json"):
        filename = path.path
        print(filename)
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                obj = json.loads(line)
                name = obj["name"]
                if can_be_russian(name):
                    # TODO: Fix this so that it supports entries with different etymologies
                    try:
                        lemma_infl_dict = get_stressed_words_from_html(
                            obj["article_body"]["html"])
                        for lemma, inflections in lemma_infl_dict.items():
                            if lemma != None:
                                word_set.add(lemma)
                                if inflections != None:
                                    word_set.update(inflections)
                    except:
                        print(f"PARSE ERROR for the word {name}")
                    
                    # if lemma != None:
                    #    word_dict[lemma] = inflections
                    # print(name)
                i += 1
                if i > 100:
                    break
        with open("ruwiktionary_extracted_words.txt", "w", encoding="utf-8") as out:
            # json.dump(word_dict, out, ensure_ascii=False, indent=0)
            out.write("\n".join(word_set))

if __name__ == "__main__":
    extract_words_from_html_dump()