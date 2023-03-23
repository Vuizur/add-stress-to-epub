from russian_text_stresser.helper_methods import load_spacy_full_with_lemmatizer


TEXT = "Но не думаю, что это может быть препятствием. Я найду решение вашей проблемы со временем, — она снова сдвинула брови."

TOOLTIP_TEMPLATE = """<a data-tooltip-id="{tooltip_id}" data-tooltip-html="{tooltip_content}">{word}</a><Tooltip id="{tooltip_id}" />"""

MORPH_MAPPING = {
    "Case=Nom": "Nominative case",
    "Case=Gen": "Genitive case",
    "Case=Dat": "Dative case",
    "Case=Acc": "Accusative case",
    "Case=Ins": "Instrumental case",
    "Case=Loc": "Locative case",
    "Case=Voc": "Vocative case",
    "Case=Par": "Partitive case",
    "Case=Abil": "Abessive case", # No idea if spacy detects it
    "Animacy=Anim": "Animate",
    "Animacy=Inan": "Inanimate",
    "Gender=Masc": "Masculine",
    "Gender=Fem": "Feminine",
    "Gender=Neut": "Neuter",
    "Number=Sing": "Singular",
    "Number=Plur": "Plural",
    "Person=First": "First person",
    "Person=Second": "Second person",
    "Person=Third": "Third person",
    "Tense=Past": "Past tense",
    "Tense=Pres": "Present tense",
    "Tense=Fut": "Future tense",
    "Aspect=Imp": "Imperfective aspect",
    "Aspect=Perf": "Perfective aspect",
    "Degree=Pos": "Positive degree",
    "Degree=Cmp": "Comparative degree",
    "Degree=Sup": "Superlative degree",
    

}

def turn_morph_into_html(morph: str):
    """Turns morph into HTML."""
    html = ""
    # Split by |
    morphs = morph.split("|")
    for morph in morphs:
        # map "Case=Nom"
        

def turn_spacy_text_into_tooltips(text: str):
    """Turns text into tooltips using spaCy."""
    nlp = load_spacy_full_with_lemmatizer()
    doc = nlp(text)
    html = ""
    for i, token in enumerate(doc):
        # Put all grammatical data into the tooltip
        tooltip_content = ""
        # POS
        tooltip_content += f"{token.pos_}\n"
        # Lemma
        tooltip_content += f"{token.lemma_}\n"
        # Tag (doesn't make sense for Russian because here it's the same as POS)
        #tooltip_content += f"{token.tag_}\n"
        # Morph
        tooltip_content += f"{token.morph}\n"
        
        tooltip_content = tooltip_content.replace("\n", "<br />")
        # Create the tooltip
        tooltip_id = i
        html += TOOLTIP_TEMPLATE.format(
            tooltip_id=tooltip_id,
            tooltip_content=tooltip_content,
            word=token.text_with_ws,
        )
    return html


if __name__ == "__main__":
    print(turn_spacy_text_into_tooltips(TEXT))
