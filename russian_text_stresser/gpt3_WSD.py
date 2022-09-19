import os
import openai
import sqlite3
import json
from stressed_cyrillic_tools import unaccentify

# JSON has format like this
# {
#    "word": "весы́",
#    "inflections": [
#      "весо́в",
#      "веса́ми",
#      "веса́х",
#      "веса́м"
#    ],
#    "definitions": [
#      "прибор для измерения массы"
#    ],
#    "grammar_info": "Существительное, неодушевлённое, мужской род, 2-е склонение (тип склонения мн. <м 1b>  по классификации А. А. Зализняка); формы ед. ч. не используются.",
#    "IPA": "vʲɪˈsɨ"
# },


class RuWiktionary:
    def __init__(
        self, russian_wiktionary_json_path: str, database_path: str = "ruwiktionary.db"
    ):
        # Read the JSON file into aSQLIte database with a table for the words, and a separate table for the inflections
        # We use an database because this will be much faster than scanning the JSON file every time
        if not os.path.isfile(database_path):
            self.conn = sqlite3.connect(database_path)
            self.cursor = self.conn.cursor()

            self.cursor.execute(
                "CREATE TABLE words (word_id INTEGER PRIMARY KEY, word TEXT, word_lower_unstressed TEXT, definitions TEXT, grammar_info TEXT, IPA TEXT)"
            )
            self.cursor.execute(
                "CREATE TABLE inflections (inflection_id INTEGER PRIMARY KEY, word_id INTEGER, inflection TEXT, inflection_lower_unstressed TEXT, FOREIGN KEY(word_id) REFERENCES words(word_id))"
            )
            with open(russian_wiktionary_json_path, "r", encoding="utf-8") as f:
                all_words = json.load(f)
                for word in all_words:
                    self.cursor.execute(
                        "INSERT INTO words (word, word_lower_unstressed, definitions, grammar_info, IPA) VALUES (?, ?, ?, ?, ?)",
                        (
                            word["word"],
                            unaccentify(word["word"].lower()),
                            json.dumps(word["definitions"], ensure_ascii=False),
                            word["grammar_info"],
                            word["IPA"],
                        ),
                    )
                    word_id = self.cursor.lastrowid
                    for inflection in word["inflections"]:
                        self.cursor.execute(
                            "INSERT INTO inflections (word_id, inflection, inflection_lower_unstressed) VALUES (?, ?, ?)",
                            (word_id, inflection, unaccentify(inflection.lower())),
                        )

            # Add index to unstressed columns
            self.cursor.execute(
                "CREATE INDEX words_lower_unstressed_index ON words (word_lower_unstressed)"
            )
            self.cursor.execute(
                "CREATE INDEX inflections_lower_unstressed_index ON inflections (inflection_lower_unstressed)"
            )
            self.conn.commit()
        else:
            self.conn = sqlite3.connect(database_path)
            self.cursor = self.conn.cursor()

    def get_entries(self, word: str) -> dict:
        """Searches for all fitting entries for an (unstressed) word in the database and returns the words and its inflections"""
        self.cursor.execute(
            "SELECT word_id, word, definitions, grammar_info, IPA FROM words WHERE word_lower_unstressed = ?",
            (unaccentify(word.lower()),),
        )
        rows = self.cursor.fetchall()

        inflection_word_ids = self.get_entries_with_inflection(word)
        if inflection_word_ids is not None:
            for word_id in inflection_word_ids:
                # Check if we already have this word_id
                if not any(word_id == row[0] for row in rows):
                    self.cursor.execute(
                        "SELECT word_id, word, definitions, grammar_info, IPA FROM words WHERE word_id = ?",
                        (word_id,),
                    )
                    rows.append(self.cursor.fetchone())

        if len(rows) == 0:
            return None
        else:
            return [
                {
                    "word": row[1],
                    "definitions": json.loads(row[2]),
                    "grammar_info": row[3],
                    "IPA": row[4],
                    "inflections": self.get_inflections(row[0]),
                }
                for row in rows
            ]

    def get_inflections(self, word_id: int) -> list:
        """Returns a list of inflections for a given word_id"""
        self.cursor.execute(
            "SELECT inflection FROM inflections WHERE word_id = ?", (word_id,)
        )
        return [row[0] for row in self.cursor.fetchall()]

    def get_entries_with_inflection(self, word: str) -> list[int]:
        """Returns all fitting entries where the word is an inflection of the base word"""
        self.cursor.execute(
            "SELECT words.word_id FROM words INNER JOIN inflections ON words.word_id = inflections.word_id WHERE inflection_lower_unstressed = ?",
            (unaccentify(word.lower()),),
        )
        rows = self.cursor.fetchall()
        if len(rows) == 0:
            return None
        else:
            return [row[0] for row in rows]


class WordSenseDisambiguator:
    def __init__(
        self, russian_wiktionary_json_path: str = "ruwiktdata_cleaned.json"
    ) -> None:
        # If openai-key.txt is not found, message the user to create it
        if not os.path.exists("openai-key.txt"):
            raise FileNotFoundError(
                "Please create openai-key.txt and put your OpenAI API key in it"
            )
        with open("openai-key.txt", "r", encoding="utf-8") as f:
            openai.api_key = f.readline().strip()

    def __del__(self):
        self.cursor.close()
        self.conn.close()

    def disambiguate(self, word: str, context: str):
        question = f"""
        "Фраза: {context}"
        Вопрос: Какое определение слова " " здесь правильное?
        # Generate options
        Ответ: 
        """


if __name__ == "__main__":
    rw = RuWiktionary("ruwiktdata_cleaned.json")

    print(rw.get_entries("леса"))
