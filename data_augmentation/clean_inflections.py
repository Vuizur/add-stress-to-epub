from data_augmentation.ruwiktionary_html_dump_extractor import EntryData


def word_is_useless_grammatical_info(word: str) -> bool:
    return word.strip() in ["одуш."]


def strip_punctuation(word: str) -> str:
    return word.strip(",.!?:;")


def clean_inflection(entry_data: EntryData) -> EntryData:
    """
    Removes inflections that are either grammatical tags or punctuation or otherwise undesired, plus remove duplicates
    """

    # Clean all inflections from punctuation
    entry_data.inflections = [strip_punctuation(
        inflection) for inflection in entry_data.inflections if strip_punctuation(inflection) != ""]

    # Remove inflections that are the same as the lemma
    entry_data.inflections = [
        inflection for inflection in entry_data.inflections if inflection != entry_data.word]
