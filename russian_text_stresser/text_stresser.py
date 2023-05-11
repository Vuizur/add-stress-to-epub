from russian_text_stresser.helper_methods import is_unimportant, load_spacy_full
from stressed_cyrillic_tools import is_acute_accented
from russian_text_stresser.russian_dictionary import RussianDictionary
import pickle


class RussianTextStresser:
    def __init__(
        self,
        db_file: str = "russian_dict.db",
        simple_cases_file: str | None = "simple_cases.pkl",
        use_large_model = False,
    ) -> None:
        self.rd = RussianDictionary(db_file, simple_cases_file)
        self._nlp = load_spacy_full(use_large_model)

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
                    if (
                        len(doc) >= i + 3
                        and doc[i + 1].text == "-"
                        and token.whitespace_ == ""
                        and doc[i + 1].whitespace_ == ""
                    ):
                        fusion_str = token.text + doc[i + 1].text + doc[i + 2].text
                        fusion_str_stressed = self.rd.get_stressed_word_and_set_yo(
                            fusion_str
                        )

                        if is_acute_accented(fusion_str_stressed):
                            result_text += fusion_str_stressed + doc[i + 2].whitespace_
                            skip_elements = 2
                            continue

                    str_wrd = self.rd.get_stressed_word_and_set_yo(
                        token.text, token.pos_, token.morph
                    )
                    result_text += str_wrd + token.whitespace_
            return result_text
        else:
            return ""
