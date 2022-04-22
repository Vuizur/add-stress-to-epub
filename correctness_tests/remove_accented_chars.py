import unicodedata

def remove_accented_chars(word: str):
    return unicodedata.normalize("NFC", word).replace("\u0301", "")
     
print(remove_accented_chars("а́лый"))