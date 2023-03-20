import json
import unicodedata

# Open the kaikki.org-dictionary-Russian.json file
with open('kaikki.org-dictionary-Russian.json', 'r', encoding='utf-8') as f:
    for line in f:
        # Load the line as a JSON object
        word_obj = json.loads(line)
        # Get the word
        word = unicodedata.normalize("NFD", word_obj['word'])
        for i in range(len(word) - 1):
            # Check if the letter at i + 1 is ´
            previous_letter = word[i]
            next_letter = word[i + 1]
            if next_letter == "\u0301" and previous_letter.lower() not in "аеиоуыэюяё":
                print(word)
