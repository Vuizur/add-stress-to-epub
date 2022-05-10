from dataclasses import dataclass
import dataclasses
import os
import json
from bs4 import BeautifulSoup, PageElement
import re

# has to contain cyrillic, but not the characters only other slavic languages have

def can_be_russian(text: str):
    text_lower = text.lower()
    return bool(re.search('[а-яА-Я]', text)) and "ў" not in text_lower and "ї" not in text_lower and "є" not in text_lower and \
        "ћ" not in text_lower and "ђ" not in text_lower and "ґ" not in text_lower and "і" not in text_lower and "қ" not in text_lower


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

    return [word.replace("буду/будешь… ", "") for word in words if word != "-" and word != "—"]

@dataclass
class EntryData:
    """Contains the data of one etymology"""
    word: str
    inflections: list[str] = dataclasses.field(default_factory=list)
    definitions: list[str] = dataclasses.field(default_factory=list)

def extract_definition_from_section(entry_data: EntryData, section: PageElement):
    """Updates the entry data with the definitions"""
    definition_el = section.find("h4", id="Значение")
    if definition_el == None:
        return
    else:
        ol = definition_el.find_next("ol")
        for li in ol.children:
            def_text = li.text
            if def_text != "" and def_text != "\n":
                entry_data.definitions.append(li.text)

def extract_stressed_words_from_section(section: PageElement) -> EntryData:
    lemma_p = section.find("p", about=True)
    lemma = get_lemma(lemma_p.b)
    entry_data = EntryData(lemma)

    morpher_table = section.find("table", {"class": "morfotable"})

    if morpher_table != None:
        entry_data.inflections.extend(get_morph_table_words(morpher_table))
    for next_sbln in section.next_siblings:
        if next_sbln.find("h3", id="Семантические_свойства"):
            extract_definition_from_section(entry_data, next_sbln.find("section"))
    return entry_data

def section_contains_two_etymologies(section):
    #h2 etc
    return section.find("h2")

def append_definition_to_entry_data(entry_data: EntryData, section_containing_lemma: PageElement):
    for next_sbln in section_containing_lemma.next_siblings:
        if next_sbln.find("h3", id="Семантические_свойства"):
            extract_definition_from_section(entry_data, next_sbln.find("section"))

def get_stressed_words_from_html(html: str) -> list[EntryData]:

    soup = BeautifulSoup(html, "lxml")
    # Important: The HTML dump pages are structured differently from the online hosted version
    inflection_dict = {}
    russian_h1 = soup.find("h1", id="Русский")
    if russian_h1 != None:
        for sibling in russian_h1.next_siblings:
            if sibling.name == "section":
                if not section_contains_two_etymologies(sibling):
                    entry_data = extract_stressed_words_from_section(sibling)
                    return [entry_data]
                else:
                    entry_data_list: list[EntryData] = []
                    for sibling in russian_h1.next_siblings:
                        if sibling.name == "section":
                            entry_data = extract_stressed_words_from_section(sibling)
                            entry_data_list.append(entry_data)
                    return entry_data_list
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
                    try:
                        entry_data_list = get_stressed_words_from_html(
                            obj["article_body"]["html"])
                        for entry_data in entry_data_list:
                            if entry_data.word != None:
                                word_set.add(entry_data.word)
                                if entry_data.inflections != None:
                                    word_set.update(entry_data.inflections)
                    except:
                        print(f"PARSE ERROR for the word {name}")
                        pass
                    
                i += 1
                if i > 100:
                    break
                #if i % 5000 == 0:
                #    print(i)
        with open("ruwiktionary_extracted_words_refactored.txt", "w", encoding="utf-8") as out:
            # json.dump(word_dict, out, ensure_ascii=False, indent=0)
            out.write("\n".join(word_set))

if __name__ == "__main__":
    extract_words_from_html_dump()