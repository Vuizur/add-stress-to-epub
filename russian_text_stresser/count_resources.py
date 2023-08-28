from dataclasses import dataclass
import json
import pandas as pd
from typing import Any, Optional
import sqlite3

@dataclass
class Resource:
    name: str
    base_words: Optional[int]
    inflections: Optional[int]
    total: Optional[int]


def print_resource_stats():

    resources: list[Resource] = []

    # Open wikipedia_words.txt
    with open('wikipedia_words.txt', 'r', encoding='utf-8') as f:
        words = f.read().splitlines()
        resources.append(Resource('Wikipedia', None, None, len(words)))
    # load openrussian.db
    #conn = sqlite3.connect('openrussian.db')
    #c = conn.cursor()
    #c.execute('SELECT COUNT(*) FROM words')
    #resources.append(Resource('OpenRussian', c.fetchone()[0], None, None))

    OPENRUSSIAN_BASE_WORDS = 84077
    OPENRUSSIAN_INFLECTION_COUNT = 946110

    resources.append(Resource('OpenRussian', OPENRUSSIAN_BASE_WORDS, OPENRUSSIAN_INFLECTION_COUNT, OPENRUSSIAN_BASE_WORDS + OPENRUSSIAN_INFLECTION_COUNT))

    # load ruwiktdata_int-old.json
    with open('ruwiktdata_cleanedЩДВ.json', 'r', encoding='utf-8') as f:
        # Load json file
        data = json.load(f)
        base_words: set[str] = set()
        inflections: set[str] = set()
        for word in data:
            base_words.add(word['word'])
            for inflection in word['inflections']:
                inflections.add(inflection)
        resources.append(Resource('Russian Wiktionary', len(base_words), len(inflections), len(base_words) + len(inflections)))

    def get_canonical_form(data: dict[str, Any]) -> str:
        if "forms" in data:
            for form in data["forms"]:
                if "canonical" in form["tags"]:
                    return form["form"]
        return data["word"]

    # Load russian-kaikki.json
    with open('russian-kaikki.json', 'r', encoding='utf-8') as f:
        base_words: set[str] = set()
        inflections: set[str] = set()

        for line in f:
            data = json.loads(line)
            # This signifies that the word is not only an inflection
            non_form_senses = [sense for sense in data["senses"] if "form_of" not in sense] 
            if len(non_form_senses) > 0:
                if "forms" in data and any("tags" in form and "canonical" in form["tags"] for form in data["forms"]):
                    base_words.add(get_canonical_form(data))
                    
                    other_forms = [form for form in data["forms"] if "canonical" not in form["tags"]]
                    for form in other_forms:
                        inflections.add(form["form"])
                else:
                    base_words.add(data["word"])
            else:
                inflections.add(get_canonical_form(data))

        resources.append(Resource('English Wiktionary (kaikki)', len(base_words), len(inflections), len(base_words) + len(inflections)))

    print(resources)
    # Turn resources into a dataframe
    df = pd.DataFrame([res.__dict__ for res in resources])#, columns=['Resource', 'Base words', 'Inflections', 'Total'])


    # Print to latex
    print(df.to_latex(index=False))

def convert_ods_to_latex():
    df = pd.read_excel("correctness_tests/pro-con-table.ods")
    print(df)
    # Replace NaN with empty string
    df = df.fillna('')
    # Remove column "Notes"
    df = df.drop(columns=['Notes'])
    # Print to latex
    print(df.to_latex(index=False))
if __name__ == '__main__':
    #print_resource_stats()
    convert_ods_to_latex()