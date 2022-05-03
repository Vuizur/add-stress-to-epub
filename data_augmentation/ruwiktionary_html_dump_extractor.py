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
        for cell in cells[1:]: # Leave out left definition cell
            
            words.extend(cell.get_text("|").split("|"))

    return words

def get_stressed_words_from_html(html: str):
    #print(html)
    #lxml is supposed to be the fastest parser
    lemma: str = None

    soup = BeautifulSoup(html, "lxml")
    # The HTML dump pages are structured differently from the online hosted version

    russian_h1 = soup.find("h1", id = "Русский")
    if russian_h1 != None:
        for sibling in russian_h1.next_siblings:
            if sibling.name == "section":
                # This is the section that contains the morph table and the lemma
                lemma_p = sibling.find("p")
                print(get_lemma(lemma_p.b))
                lemma = get_lemma(lemma_p.b)
                
                morpher_table = sibling.find("table", {"class": "morfotable"})
                if morpher_table != None:
                    morph_table_words = get_morph_table_words(morpher_table)
                    print(morph_table_words)
                break
                



def extract_words_from_html_dump():
    #pathlist = Path("D:/ruwiktionary-NS0-20220501-ENTERPRISE-HTML.json").rglob(".*")

    i = 0
    for path in os.scandir("D:/ruwiktionary-NS0-20220501-ENTERPRISE-HTML.json"):
        filename = path.path
        print(filename)
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                obj = json.loads(line)
                name = obj["name"]
                if can_be_russian(name):
                    get_stressed_words_from_html(obj["article_body"]["html"])
                    print(name)
                i += 1
                if i > 100:
                    quit()

if __name__ == "__main__":
    extract_words_from_html_dump()