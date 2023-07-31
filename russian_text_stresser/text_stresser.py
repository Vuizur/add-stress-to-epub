from typing import Any, Optional
from russian_text_stresser.helper_methods import is_unimportant, load_spacy_full
from stressed_cyrillic_tools import is_acute_accented
from russian_text_stresser.russian_dictionary import RussianDictionary
from russian_text_stresser.benchmark_word_sense_disambiguation import LocalLLM
from russian_text_stresser.gpt3_WSD import WordSenseDisambiguator


class RussianTextStresser:
    def __init__(
        self,
        db_file: str = "russian_dict.db",
        simple_cases_file: Optional[str] = "simple_cases.pkl",
        use_large_model=False,
        llm: Optional[LocalLLM] = None, #
    ) -> None:
        self.rd = RussianDictionary(db_file, simple_cases_file)
        self._nlp = load_spacy_full(use_large_model)
        if llm is not None:
            self.wsd = WordSenseDisambiguator(llm)
        else:
            self.wsd = None

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

                        if is_acute_accented(fusion_str_stressed): # TODO: Maybe also check ё
                            result_text += fusion_str_stressed + doc[i + 2].whitespace_
                            skip_elements = 2
                            continue

                    str_wrd = self.rd.get_stressed_word_and_set_yo(
                        token.text, token.pos_, token.morph
                    )
                    result_text += str_wrd + token.whitespace_

            if self.wsd is not None:
                result_text = self.wsd.detect_and_fix_missing_stressed_words(result_text)
            return result_text
        else:
            return ""
