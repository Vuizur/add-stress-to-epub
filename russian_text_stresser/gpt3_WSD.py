import os
import openai


class WordSenseDisambiguator:
    def __init__(self) -> None:
        # If openai-key.txt is not found, message the user to create it
        if not os.path.exists("openai-key.txt"):
            raise FileNotFoundError("Please create openai-key.txt and put your OpenAI API key in it")
        with open("openai-key.txt", "r", encoding="utf-8") as f:
            openai.api_key = f.readline().strip()

    def disambiguate(self, word: str, context: str):
        question = f"""
        "Фраза: {context}"
        Вопрос: Какое определение слова " " здесь правильное?
        # Generate options
        Ответ: 
        """


        