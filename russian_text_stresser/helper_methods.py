from pathlib import Path

from spacy import Language, load


def load_spacy_full() -> Language:
    bundle_dir = Path(__file__).parent.absolute()

    return load(bundle_dir / "ru_core_news_sm-3.4.0", exclude=["lemmatizer", "ner"])

def load_spacy_full_with_lemmatizer() -> Language:
    bundle_dir = Path(__file__).parent.absolute()

    return load(bundle_dir / "ru_core_news_sm-3.4.0", exclude=["ner"])
def load_spacy_min() -> Language:
    bundle_dir = Path(__file__).parent.absolute()
    return load(
        bundle_dir / "ru_core_news_sm-3.4.0",
        exclude=[
            "tok2vec",
            "morphologizer",
            "parser",
            "senter",
            "attribute_ruler",
            "lemmatizer",
            "ner",
        ],
    )


def is_unimportant(token):
    return (
        token.pos_ == "PUNCT"
        or token.pos_ == "SYM"
        or token.pos_ == "X"
        or token.pos_ == "SPACE"
        or token.text == "-"
    )
