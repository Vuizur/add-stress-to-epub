from pathlib import Path
from spacy import load
from helper_methods import is_acute_accented, is_unimportant, load_spacy_full
from russian_dictionary import RussianDictionary

class RussianTextStresser:

    def __init__(self) -> None:
        self.rd = RussianDictionary()
        self._nlp = load_spacy_full()
    def stress_text(self, text: str) -> str:
        if len(text) > 0:
            result_text = ""
            doc = self._nlp(text)
            skip_elements = 0
            for i, token in enumerate(doc):
                if skip_elements > 0:
                    skip_elements -= 1
                    continue
                if is_unimportant(token):
                    result_text += token.text_with_ws
                else:
                    if len(doc) >= i + 3 and doc[i + 1].text == "-" and token.whitespace_ == "" and doc[i + 1].whitespace_ == "":
                        fusion_str = token.text + doc[i + 1].text + doc[i + 2].text
                        fusion_str_stressed = self.rd.get_stressed_word_and_set_yo(fusion_str)

                        if is_acute_accented(fusion_str_stressed):
                            result_text += fusion_str_stressed + doc[i + 2].whitespace_
                            skip_elements = 2
                            continue                           
        
                    str_wrd = self.rd.get_stressed_word_and_set_yo(token.text, token.pos_, token.morph)
                    result_text += str_wrd + token.whitespace_
            return result_text
        else:
            return ""