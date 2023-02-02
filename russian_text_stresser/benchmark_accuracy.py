from dataclasses import dataclass
import os
from pathlib import Path
from helper_methods import load_spacy_full, load_spacy_min
from stressed_cyrillic_tools import (
    has_acute_accent_or_only_one_syllable,
    remove_accent_if_only_one_syllable,
    unaccentify,
    remove_yo
)
from text_stresser import RussianTextStresser
from spacy.tokens.token import Token
from russian_stress_benchmark import benchmark_everything_in_folder

@dataclass
class StressMistake:
    orig_token: str
    auto_stressed_token: str
    sentence: str
    unstressed_token_with_grammar_info: Token # This should include grammar info an
@dataclass
class AnalysisResults:
    orig_doc_length: int
    auto_stressed_doc_length: int
    num_unstressed_tokens: int
    num_correctly_stressed_tokens: int
    num_incorrectly_stressed_tokens: int
    stress_mistakes: list[StressMistake]
    file_path: str | list[str]

    def get_percentage_unstressed_tokens(self) -> float:
        return self.num_unstressed_tokens / self.orig_doc_length * 100
    def get_percentage_correctly_stressed_tokens(self) -> float:
        return self.num_correctly_stressed_tokens / self.orig_doc_length * 100
    def get_percentage_incorrectly_stressed_tokens(self) -> float:
        return self.num_incorrectly_stressed_tokens / self.orig_doc_length * 100
    # Overload the + operator to make it easier to combine results
    
    def __add__(self, other):

        if isinstance(self.file_path, str):
            self.file_path = [self.file_path]
        if isinstance(other.file_path, str):
            other.file_path = [other.file_path]

        return AnalysisResults(
            self.orig_doc_length + other.orig_doc_length,
            self.auto_stressed_doc_length + other.auto_stressed_doc_length,
            self.num_unstressed_tokens + other.num_unstressed_tokens,
            self.num_correctly_stressed_tokens + other.num_correctly_stressed_tokens,
            self.num_incorrectly_stressed_tokens + other.num_incorrectly_stressed_tokens,
            self.stress_mistakes + other.stress_mistakes,
            self.file_path + other.file_path,
        )

class AccuracyCalculator:
    def __init__(self) -> None:
        # self._nlp = load_spacy_min()
        self._nlp = (
            load_spacy_full()
        )  # We need this because we want to collect part of speech/morphology statistics

    def calc_accuracy(
        self, orig_stressed_file_path: str, auto_stressed_file_path: str, remove_yo: bool = False
    ) -> AnalysisResults:
        with open(orig_stressed_file_path, "r", encoding="utf-8") as orig_file, open(
            auto_stressed_file_path, "r", encoding="utf-8"
        ) as auto_stressed_file:
            orig_text = orig_file.read()
            auto_stressed_text = auto_stressed_file.read()
            orig_text_fixed = remove_accent_if_only_one_syllable(orig_text)
            orig_doc = self._nlp(orig_text_fixed)
            auto_stress_doc = self._nlp(auto_stressed_text)
            if remove_yo:
                unstressed_text = unaccentify(remove_yo(orig_text))
            else:
                unstressed_text = unaccentify(orig_text)
            unstressed_doc = self._nlp(unstressed_text)

            num_tokens_in_original = len(orig_doc)
            num_tokens_in_auto_stressed = len(auto_stress_doc)
            stress_mistakes: list[StressMistake] = []

            if num_tokens_in_auto_stressed != num_tokens_in_original:
                print(
                    f"Error!\nLength of original document: {num_tokens_in_original}\nLength of automatically stressed document: {num_tokens_in_auto_stressed}"
                )
            num_unstressed_tokens = 0
            num_correctly_stressed_tokens = 0

            for i, orig_token in enumerate(orig_doc):

                auto_stress_token = auto_stress_doc[i]
                orig_token_text: str = orig_token.text
                auto_stress_token_text: str = auto_stress_token.text
                if unaccentify(orig_token_text) != unaccentify(auto_stress_token_text):
                    print("Differing words:")
                    print(orig_token.text)
                    print(auto_stress_token.text)

                if not has_acute_accent_or_only_one_syllable(auto_stress_token_text):
                    num_unstressed_tokens += 1
                else:
                    if orig_token_text == auto_stress_token_text:
                        num_correctly_stressed_tokens += 1
                    else:
                        stress_mistakes.append(
                            StressMistake(
                                orig_token_text,
                                auto_stress_token_text,
                                orig_token.sent.text,
                                unstressed_doc[i], # We take here the unstressed doc because I doubt
                                # that spaCy will perform correct grammar analysis for stressed texts
                            )
                        )

            num_incorrectly_stressed_tokens = (
                num_tokens_in_original
                - num_correctly_stressed_tokens
                - num_unstressed_tokens
            )

            analysis_results = AnalysisResults(
                num_tokens_in_original,
                num_tokens_in_auto_stressed,
                num_unstressed_tokens, # / num_tokens_in_original * 100,
                num_correctly_stressed_tokens, #/ num_tokens_in_original * 100,
                num_incorrectly_stressed_tokens, # / num_tokens_in_original * 100,
                stress_mistakes,
                orig_stressed_file_path,
            )
            return analysis_results

    def calc_accuracy_over_dir(self, original_dir_path: str, auto_stressed_dir_path: str)-> AnalysisResults:
        # Iterate over all files in the directory and subdirectories
        results: list[AnalysisResults] = []
        for root, dirs, files in os.walk(original_dir_path):
            for file in files:
                if file.endswith(".txt") or file.endswith(".ref"):
                    original_file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(original_file_path, original_dir_path)
                    #auto_stressed_file_path = os.path.join(auto_stressed_dir_path, file)
                    auto_stressed_file_path = os.path.join(auto_stressed_dir_path, relative_path)
                    results.append(self.calc_accuracy(original_file_path, auto_stressed_file_path))
        return sum(results)

    def print_accuracy(self, original_file_path, auto_stressed_file_path):
        analysis_res = self.calc_accuracy(original_file_path, auto_stressed_file_path)
        print(f"Number of tokens: {analysis_res.orig_doc_length}")
        print(
            f"Percentage correctly stressed tokens: {analysis_res.percentage_correctly_stressed_tokens}"
        )
        print(
            f"Percentage unstressed tokens: {analysis_res.percentage_unstressed_tokens}"
        )
        print(
            f"Percentage incorrectly stressed tokens: {analysis_res.percentage_incorrectly_stressed_tokens}"
        )


def benchmark_accuracy(file_path: str):
    # raise deprecation warning
    raise DeprecationWarning(
        "This function is deprecated and will be removed in the future. Use AccuracyCalculator instead."
    )

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
    with open(
        f"../correctness_tests/results/{file_name_stump}_original.txt",
        "w",
        encoding="utf-8",
    ) as orig, open(
        f"../correctness_tests/results/{file_name_stump}_edit.txt",
        "w",
        encoding="utf-8",
    ) as edit:
        orig.write(text_file)
        edit.write(stressed_file)

def print_statistics_over_data(folder_path: str):
    nlp = load_spacy_full()

    token_num = 0
    # Iterate over all files in the folder and its subfolders
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".txt") or file.endswith(".ref"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
                    doc = nlp(text)
                    token_num += len(doc)

    print(f"Number of tokens: {token_num}")

def perform_benchmark_for_my_solution() -> None:
    ts = RussianTextStresser()
    base_folder = "correctness_tests"
    orig_folder = "stressed_russian_texts"
    result_folder = "result_my_solution"

    base_path = f"{base_folder}/{orig_folder}" 
    result_path = f"{base_folder}/{result_folder}" 
    
    benchmark_everything_in_folder(base_path, result_path, ts.stress_text)

if __name__ == "__main__":

    perform_benchmark_for_my_solution()
    quit()

    #print_statistics_over_data("correctness_tests/stressed_russian_texts")
    #quit()
    
    acc_calc = AccuracyCalculator()

    # orig_path = Path(__file__).parent.parent / "correctness_tests" / "results" / "bargamot_original.txt"
    acc_calc.print_accuracy(
        "correctness_tests/results/bargamot_original.txt",
        "correctness_tests/results/bargamot_edit.txt",
    )

