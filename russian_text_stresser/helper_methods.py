from pathlib import Path
import unicodedata

from spacy import Language, load

def load_spacy_full() -> Language:
    bundle_dir = Path(__file__).parent.absolute()
    return load(bundle_dir / "ru_core_news_sm-3.3.0")

def load_spacy_min() -> Language:
    bundle_dir = Path(__file__).parent.absolute()
    return load(bundle_dir / "ru_core_news_sm-3.3.0", exclude=[
        "tok2vec", "morphologizer", "parser", "senter", "attribute_ruler", "lemmatizer", "ner"])

def is_unimportant(token):
    return token.pos_ == "PUNCT" or token.pos_ == "SYM" or token.pos_ == "X" or token.pos_ == "SPACE" or token.text == "-"

def is_acute_accented(phrase: str):
    for char in phrase:
        if char == u'\u0301':
            return True
    return False

def has_only_one_syllable(word: str):
    word_lower = word.lower()
    vowels = 0
    for char in word_lower:
        if char in "аоэуыяеёюи":
            vowels += 1
    return vowels <= 1

def has_acute_accent_or_only_one_syllable(word: str):
    return is_acute_accented(word) or has_only_one_syllable(word)

ACCENT_MAPPING = {
    '́': '',
    '̀': '',
    'а́': 'а',
    'а̀': 'а',
    'е́': 'е',
    'ѐ': 'е',
    'и́': 'и',
    'ѝ': 'и',
    'о́': 'о',
    'о̀': 'о',
    'у́': 'у',
    'у̀': 'у',
    'ы́': 'ы',
    'ы̀': 'ы',
    'э́': 'э',
    'э̀': 'э',
    'ю́': 'ю',
    '̀ю': 'ю',
    'я́́': 'я',
    'я̀': 'я',
}

ACCENT_MAPPING = {unicodedata.normalize(
    'NFKC', i): j for i, j in ACCENT_MAPPING.items()}


def unaccentify(s):
    source = unicodedata.normalize('NFKC', s)
    for old, new in ACCENT_MAPPING.items():
        source = source.replace(old, new)
    return source


def remove_accent_if_only_one_syllable(s: str):
    """Removes the accent from words like что́. Also works with complete texts (splits by space)"""
    if " " in s:
        words = s.split(" ")
        fixed_words = []
        for word in words:
            fixed_words.append(remove_accent_if_only_one_syllable(word))
        return " ".join(fixed_words)

    s_unaccented = unaccentify(s)
    if has_only_one_syllable(s_unaccented):
        return s_unaccented
    else:
        return s
