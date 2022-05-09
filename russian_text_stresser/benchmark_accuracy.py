
from os import path
import sys

from dataclasses import dataclass
from pathlib import Path
from spacy import load
from helper_methods import has_acute_accent_or_only_one_syllable, is_acute_accented, remove_accent_if_only_one_syllable, unaccentify
from text_stresser import RussianTextStresser

@dataclass
class AnalysisResults:
    orig_doc_length: int
    auto_stressed_doc_length: int
    percentage_unstressed_tokens: float
    percentage_correctly_stressed_tokens: float
    percentage_incorrectly_stressed_tokens: float

class AccuracyCalculator:
    def __init__(self) -> None:
        bundle_dir = Path(__file__).parent.absolute()

        self._nlp = load(bundle_dir / "ru_core_news_sm-3.1.0", exclude=[
            "tok2vec", "morphologizer", "parser", "senter", "attribute_ruler", "lemmatizer", "ner"])

    def calc_accuracy(self, orig_stressed_file_path: str, auto_stressed_file_path: str) -> AnalysisResults:
        with open(orig_stressed_file_path, "r", encoding="utf-8") as orig_file, \
                open(auto_stressed_file_path, "r", encoding="utf-8") as auto_stressed_file:
            orig_text = orig_file.read()
            auto_stressed_text = auto_stressed_file.read()
            orig_text_fixed = remove_accent_if_only_one_syllable(orig_text)
            orig_doc = self._nlp(orig_text_fixed)
            auto_stress_doc = self._nlp(auto_stressed_text)
            num_tokens_in_original = len(orig_doc)
            num_tokens_in_auto_stressed = len(auto_stress_doc)
            if num_tokens_in_auto_stressed != num_tokens_in_original:
                print(
                    f"Error!\nLength of original document: {num_tokens_in_original}\nLength of automatically stressed document: {num_tokens_in_auto_stressed}")
            num_unstressed_tokens = 0
            num_correctly_stressed_tokens = 0
            auto_stress_offset = 0
            skip_next_token = False
            for i, orig_token in enumerate(orig_doc):
                if skip_next_token:
                    skip_next_token = False
                    continue
                auto_stress_token = auto_stress_doc[i + auto_stress_offset]
                orig_token_text: str = orig_token.text
                auto_stress_token_text: str = auto_stress_token.text
                if unaccentify(orig_token_text) != unaccentify(auto_stress_token_text):
                    # Spacy's tokenization algorithm is buggy so this can happen in some cases, because it does not split the dot when the last character is accented
                    print("Differing words:")
                    print(orig_token.text)
                    print(auto_stress_token.text)
                    if unaccentify(orig_token_text) < unaccentify(auto_stress_token_text):
                        # For this we assume that something got split from the original token, but not from the auto stress
                        skip_next_token = True
                        auto_stress_offset += -1
                        # This is according to the one error case
                        auto_stress_token_text.strip(".")

                if not has_acute_accent_or_only_one_syllable(auto_stress_token_text):
                    num_unstressed_tokens += 1
                else:
                    if orig_token_text == auto_stress_token_text:
                        num_correctly_stressed_tokens += 1
            num_incorrectly_stressed_tokens = num_tokens_in_original - \
                num_correctly_stressed_tokens - num_unstressed_tokens

            analysis_results = AnalysisResults(
                num_tokens_in_original,
                num_tokens_in_auto_stressed,
                num_unstressed_tokens / num_tokens_in_original * 100,
                num_correctly_stressed_tokens / num_tokens_in_original * 100,
                num_incorrectly_stressed_tokens / num_tokens_in_original * 100
            )
            #analysis_results.auto_stressed_doc_length = num_tokens_in_auto_stressed
            #analysis_results.orig_doc_length = num_tokens_in_original
            #analysis_results.percentage_correctly_stressed_tokens = num_correctly_stressed_tokens / \
            #    num_tokens_in_original * 100
            #analysis_results.percentage_incorrectly_stressed_tokens = num_incorrectly_stressed_tokens / \
            #    num_tokens_in_original * 100
            #analysis_results.percentage_unstressed_tokens = num_unstressed_tokens / \
            #    num_tokens_in_original * 100
            return analysis_results


    def print_accuracy(self, original_file_path, auto_stressed_file_path):
        analysis_res = self.calc_accuracy(original_file_path, auto_stressed_file_path)
        print(f"Number of tokens: {analysis_res.orig_doc_length}")
        print(f"Percentage correctly stressed tokens: {analysis_res.percentage_correctly_stressed_tokens}")
        print(f"Percentage unstressed tokens: {analysis_res.percentage_unstressed_tokens}")
        print(f"Percentage incorrectly stressed tokens: {analysis_res.percentage_incorrectly_stressed_tokens}")


def benchmark_accuracy(file_path: str):
    stresser = RussianTextStresser()
    with open(file_path, "r", encoding="utf-8") as file:
        text_file = file.read()
        text_file = remove_accent_if_only_one_syllable(text_file)
        text_file_unstressed = unaccentify(text_file)
        split_file_as_it_should_be = text_file.split(" ")
        stressed_file = stresser.stress_text(text_file_unstressed)
        split_file_by_my_program = stressed_file.split(" ")
    correct_tokens = 0
    wrong_tokens = 0
    
    for i in range(0, len(split_file_as_it_should_be)):
        # The stress of one-syllable words is obvious and usually not marked
        if split_file_as_it_should_be[i] == split_file_by_my_program[i]:
            correct_tokens += 1
        else:
            wrong_tokens += 1
            print(split_file_as_it_should_be[i])
            print(split_file_by_my_program[i])
    print(correct_tokens)
    print(wrong_tokens)
    file_name = file_path.split("/")[-1]
    file_name_stump = file_name.split(".")[0]
    with open(f"../correctness_tests/results/{file_name_stump}_original.txt", "w", encoding="utf-8") as orig, \
            open(f"../correctness_tests/results/{file_name_stump}_edit.txt", "w", encoding="utf-8") as edit:
        orig.write(text_file)
        edit.write(stressed_file)

if __name__ == "__main__":
    acc_calc = AccuracyCalculator()

    #orig_path = Path(__file__).parent.parent / "correctness_tests" / "results" / "bargamot_original.txt"
    acc_calc.print_accuracy("correctness_tests/results/bargamot_original.txt", "correctness_tests/results/bargamot_edit.txt")