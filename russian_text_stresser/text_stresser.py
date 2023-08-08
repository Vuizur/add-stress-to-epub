from typing import Any, Optional
from russian_text_stresser.helper_methods import is_unimportant, load_spacy_full
from stressed_cyrillic_tools import (
    is_acute_accented,
    has_acute_accent_or_only_one_syllable,
)
from russian_text_stresser.russian_dictionary import RussianDictionary
try:
    from russian_text_stresser.gpt3_WSD import LocalLLM, WordSenseDisambiguator
except ImportError:
    pass


class RussianTextStresser:
    def __init__(
        self,
        db_file: str = "russian_dict.db",
        simple_cases_file: Optional[str] = "simple_cases.pkl",
        use_large_model=False,
        llm: Optional["LocalLLM"] = None,  #
        add_stressrnn: bool = False,
        stressrnn_threshold: float = 0.8,
    ) -> None:
        self.rd = RussianDictionary(db_file, simple_cases_file)
        self._nlp = load_spacy_full(use_large_model)
        if llm is not None:
            self.wsd = WordSenseDisambiguator(llm)
        else:
            self.wsd = None
        if add_stressrnn:
            try:
                from stressrnn import StressRNN

                self.stress_rnn = StressRNN()
            except ImportError:
                print("Please install the stressrn extra to use the stressrnn model.")
                self.stress_rnn = None
            self.stressrnn_threshold = stressrnn_threshold
        else:
            self.stress_rnn = None

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

                        if is_acute_accented(
                            fusion_str_stressed
                        ):  # TODO: Maybe also check ё
                            result_text += fusion_str_stressed + doc[i + 2].whitespace_
                            skip_elements = 2
                            continue

                    str_wrd = self.rd.get_stressed_word_and_set_yo(
                        token.text, token.pos_, token.morph
                    )
                    result_text += str_wrd + token.whitespace_

            if self.wsd is not None:
                result_text = self.wsd.detect_and_fix_missing_stressed_words(
                    result_text
                )

            if self.stress_rnn is not None:
                final_text = ""
                rnn_stressed_text = self.stress_rnn.put_stress(
                    result_text,
                    accuracy_threshold=self.stressrnn_threshold,
                    replace_similar_symbols=False,
                    lemmatize_words=False,
                )
                # Replace the + with the stress symbol
                rnn_stressed_text = rnn_stressed_text.replace("+", "́")
                with self._nlp.select_pipes(enable=[]):
                    my_stressed_doc = self._nlp(result_text)
                    rnn_stressed_doc = self._nlp(rnn_stressed_text)
                    if len(my_stressed_doc) != len(rnn_stressed_doc):
                        print(
                            "Warning: The number of tokens in the original text and the stressrnn text do not match."
                        )
                        print("Original text: ", result_text)
                        print("Stressrnn text: ", rnn_stressed_text)
                        return result_text
                    for my_token, rnn_token in zip(my_stressed_doc, rnn_stressed_doc):
                        if (
                            has_acute_accent_or_only_one_syllable(my_token.text)
                            or "ё" in my_token.text
                            or "Ё" in my_token.text
                        ):
                            final_text += my_token.text_with_ws
                        else:
                            final_text += rnn_token.text_with_ws

                return final_text
            return result_text
        else:
            return ""
