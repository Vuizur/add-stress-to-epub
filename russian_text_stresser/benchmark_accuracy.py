from collections import defaultdict
from dataclasses import dataclass
import os
from pathlib import Path
import random
from debug_helpers import (
    esc_nl,
    print_spacy_doc_difference,
    print_two_docs_with_pos_next_to_another,
)
from helper_methods import load_spacy_full, load_spacy_min
from stressed_cyrillic_tools import (
    has_acute_accent_or_only_one_syllable,
    remove_accent_if_only_one_syllable,
    unaccentify,
    remove_yo,
    has_only_one_syllable,
)
from text_stresser import RussianTextStresser
from spacy.tokens.token import Token
from russian_stress_benchmark import benchmark_everything_in_folder
from pprint import pprint
from russtress import Accent
import csv
from russ.stress.predictor import StressPredictor


def add_defaultdicts(dict1, dict2):
    for key in dict2:
        dict1[key] += dict2[key]
    return dict1


@dataclass
class StressMistake:
    orig_token: str
    auto_stressed_token: str
    sentence: str
    unstressed_token_with_grammar_info: Token  # This should include grammar info an


@dataclass
class AnalysisResults:
    orig_doc_length: int
    auto_stressed_doc_length: int
    num_unstressed_tokens: int
    num_correctly_stressed_tokens: int
    num_incorrectly_stressed_tokens: int
    num_correctly_stressed_by_pos: defaultdict[str, int]
    num_unstressed_by_pos: defaultdict[str, int]
    num_incorrectly_stressed_by_pos: defaultdict[str, int]
    stress_mistakes: list[StressMistake]
    file_path: str | list[str]

    def get_percentage_unstressed_tokens(self) -> float:
        return self.num_unstressed_tokens / self.orig_doc_length * 100

    def get_percentage_correctly_stressed_tokens(self) -> float:
        return self.num_correctly_stressed_tokens / self.orig_doc_length * 100

    def get_percentage_incorrectly_stressed_tokens(self) -> float:
        return self.num_incorrectly_stressed_tokens / self.orig_doc_length * 100

    def get_percentage_correctly_stressed_by_pos(self) -> dict[str, float]:
        return {
            pos: self.num_correctly_stressed_by_pos[pos]
            / (
                self.num_correctly_stressed_by_pos[pos]
                + self.num_incorrectly_stressed_by_pos[pos]
                + self.num_unstressed_by_pos[pos]
            )
            * 100
            for pos in self.num_correctly_stressed_by_pos
        }

    def get_percentage_unstressed_by_pos(self) -> dict[str, float]:
        return {
            pos: self.num_unstressed_by_pos[pos]
            / (
                self.num_correctly_stressed_by_pos[pos]
                + self.num_incorrectly_stressed_by_pos[pos]
                + self.num_unstressed_by_pos[pos]
            )
            * 100
            for pos in self.num_unstressed_by_pos
        }

    def get_percentage_incorrectly_stressed_by_pos(self) -> dict[str, float]:
        return {
            pos: self.num_incorrectly_stressed_by_pos[pos]
            / (
                self.num_correctly_stressed_by_pos[pos]
                + self.num_incorrectly_stressed_by_pos[pos]
                + self.num_unstressed_by_pos[pos]
            )
            * 100
            for pos in self.num_incorrectly_stressed_by_pos
        }

    def get_all_occuring_pos(self) -> list[str]:
        return list(self.num_correctly_stressed_by_pos.keys())

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
            self.num_incorrectly_stressed_tokens
            + other.num_incorrectly_stressed_tokens,
            add_defaultdicts(
                self.num_correctly_stressed_by_pos, other.num_correctly_stressed_by_pos
            ),
            add_defaultdicts(self.num_unstressed_by_pos, other.num_unstressed_by_pos),
            add_defaultdicts(
                self.num_incorrectly_stressed_by_pos,
                other.num_incorrectly_stressed_by_pos,
            ),
            self.stress_mistakes + other.stress_mistakes,
            self.file_path + other.file_path,
        )

    # Returns empty AnalysisResults object
    @staticmethod
    def get_empty_results():
        return AnalysisResults(
            0,
            0,
            0,
            0,
            0,
            defaultdict(int),
            defaultdict(int),
            defaultdict(int),
            [],
            [],
        )


def token_is_unimportant(token: Token) -> bool:
    # We don't want to count punctuation or spaces. Also we only want takens that contain at least one letter
    return (
        token.is_punct
        or token.is_space
        or not any(char.isalpha() for char in token.text)
    )


class AccuracyCalculator:
    def __init__(self) -> None:
        # self._nlp = load_spacy_min()
        self._nlp = (
            load_spacy_full()
        )  # We need this because we want to collect part of speech/morphology statistics

    def calc_accuracy(
        self,
        orig_stressed_file_path: str,
        auto_stressed_file_path: str,
        remov_yo: bool = False,  # I am not sure if remove_yo here makes sense
    ) -> AnalysisResults:
        with open(orig_stressed_file_path, "r", encoding="utf-8") as orig_file, open(
            auto_stressed_file_path, "r", encoding="utf-8"
        ) as auto_stressed_file:
            orig_text = orig_file.read()
            auto_stressed_text = remove_accent_if_only_one_syllable(
                auto_stressed_file.read()
            )
            orig_text_fixed = remove_accent_if_only_one_syllable(orig_text)
            orig_doc = self._nlp(orig_text_fixed)
            auto_stress_doc = self._nlp(auto_stressed_text)
            if remov_yo:
                unstressed_text = unaccentify(remove_yo(orig_text))
            else:
                unstressed_text = unaccentify(orig_text)
            unstressed_doc = self._nlp(unstressed_text)

            original_no_punct_tokens = [
                token for token in orig_doc if not token_is_unimportant(token)
            ]
            auto_stressed_no_punct_tokens = [
                token for token in auto_stress_doc if not token_is_unimportant(token)
            ]
            unstressed_no_punct_tokens = [
                token for token in unstressed_doc if not token_is_unimportant(token)
            ]

            num_tokens_in_original = len(original_no_punct_tokens)
            num_tokens_in_auto_stressed = len(auto_stressed_no_punct_tokens)

            stress_mistakes: list[StressMistake] = []
            correctly_stressed_by_pos_dict: defaultdict[str, int] = defaultdict(int)
            unstressed_by_pos_dict: defaultdict[str, int] = defaultdict(int)
            incorrectly_stressed_by_pos_dict: defaultdict[str, int] = defaultdict(int)

            if num_tokens_in_auto_stressed != num_tokens_in_original:
                print(
                    f"{orig_stressed_file_path} and {auto_stressed_file_path} are not the same length."
                    f"Error!\nLength of original document: {num_tokens_in_original}\nLength of automatically stressed document: {num_tokens_in_auto_stressed}"
                )

                print_two_docs_with_pos_next_to_another(  # This is super useful for debugging
                    original_no_punct_tokens, auto_stressed_no_punct_tokens
                )
                raise Exception(
                    f"{orig_stressed_file_path} and {auto_stressed_file_path} are not the same length."
                )

            num_unstressed_tokens = 0
            num_correctly_stressed_tokens = 0
            num_differing_tokens = 0 # This means serious problems

            for orig_token, auto_stress_token, unstressed_token in zip(
                original_no_punct_tokens,
                auto_stressed_no_punct_tokens,
                unstressed_no_punct_tokens,
            ):
                # We also use the unstressed token because spaCy has better grammar analysis for unstressed tokens
                orig_token_text: str = orig_token.text
                auto_stress_token_text: str = auto_stress_token.text
                if remove_yo(unaccentify(orig_token_text)) != remove_yo(
                    unaccentify(auto_stress_token_text)
                ):
                    print("Differing words:")
                    print(orig_token.text)
                    print(auto_stress_token.text)
                    
                    num_differing_tokens += 1

                if not has_acute_accent_or_only_one_syllable(auto_stress_token_text):
                    num_unstressed_tokens += 1
                    unstressed_by_pos_dict[unstressed_token.pos_] += 1
                else:
                    if orig_token_text == auto_stress_token_text:
                        num_correctly_stressed_tokens += 1
                        correctly_stressed_by_pos_dict[unstressed_token.pos_] += 1
                    else:
                        incorrectly_stressed_by_pos_dict[unstressed_token.pos_] += 1
                        stress_mistakes.append(
                            StressMistake(
                                orig_token_text,
                                auto_stress_token_text,
                                orig_token.sent.text,
                                unstressed_token,  # We take here the unstressed doc because I doubt
                                # that spaCy will perform correct grammar analysis for stressed texts
                            )
                        )

            num_incorrectly_stressed_tokens = (
                num_tokens_in_original
                - num_correctly_stressed_tokens
                - num_unstressed_tokens
            )

            if num_differing_tokens > 0:
                print("Differing tokens: ", num_differing_tokens)
                orig_filename = os.path.basename(orig_stressed_file_path)
                auto_stressed_path_first_folder = Path(auto_stressed_file_path).parent.name
                print_two_docs_with_pos_next_to_another(  # This is super useful for debugging
                    original_no_punct_tokens, auto_stressed_no_punct_tokens,
                    f"{orig_filename}_{auto_stressed_path_first_folder}.tsv"
                )


            analysis_results = AnalysisResults(
                num_tokens_in_original,
                num_tokens_in_auto_stressed,
                num_unstressed_tokens,  # / num_tokens_in_original * 100,
                num_correctly_stressed_tokens,  # / num_tokens_in_original * 100,
                num_incorrectly_stressed_tokens,  # / num_tokens_in_original * 100,
                correctly_stressed_by_pos_dict,
                unstressed_by_pos_dict,
                incorrectly_stressed_by_pos_dict,
                stress_mistakes,
                orig_stressed_file_path,
            )
            return analysis_results

    def calc_accuracy_over_dir(
        self, original_dir_path: str, auto_stressed_dir_path: str
    ) -> list[AnalysisResults]:
        # Iterate over all files in the directory and subdirectories
        results: list[AnalysisResults] = []
        for root, dirs, files in os.walk(original_dir_path):
            for file in files:
                if file.endswith(".txt") or file.endswith(".ref"):
                    original_file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(
                        original_file_path, original_dir_path
                    )
                    # auto_stressed_file_path = os.path.join(auto_stressed_dir_path, file)
                    auto_stressed_file_path = os.path.join(
                        auto_stressed_dir_path, relative_path
                    )
                    results.append(
                        self.calc_accuracy(original_file_path, auto_stressed_file_path)
                    )
        return results

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


TEST_RG_TEXT = """
– Ты, дя́дя, мно́го не спра́шивай, – улыбну́лась де́вочка. По э́той улы́бке он по́нял, что вопро́сы действи́тельно задава́ть не ну́жно. – Ты спи́чку бе́ри|бери́.
Дя́дя закры́л глаза́ и взял чёрную спи́чку.
"""


def fix_russiangram_text(text: str) -> str:
    """If russiangram is unsure or there are two options, it returns option1|option2. We always take the first one for a fair benchmark."""
    nlp = load_spacy_min()

    doc = nlp(text)
    final_text = ""
    for token in doc:
        if "|" in token.text:
            fixed_word = token.text.split("|")[0]
            final_text += fixed_word + token.whitespace_
        else:
            final_text += token.text_with_ws
    return final_text


def fix_russiangram_folder(input_folder: str, output_folder: str) -> None:
    """Fixes all files in a folder and its subfolders"""
    # Iterate over all files in the folder and its subfolders
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith(".txt") or file.endswith(".ref"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
                    text_fixed = fix_russiangram_text(text)
                relative_path = os.path.relpath(file_path, input_folder)
                output_file_path = os.path.join(output_folder, relative_path)
                os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
                with open(output_file_path, "w", encoding="utf-8") as f:
                    f.write(text_fixed)


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
    result_folder = "results_my_solution"

    base_path = f"{base_folder}/{orig_folder}"
    result_path = f"{base_folder}/{result_folder}"

    benchmark_everything_in_folder(base_path, result_path, ts.stress_text)

def perform_benchmark_for_my_solution_old() -> None:
    ts = RussianTextStresser(db_file="russian_dict_old_downloadable.db")
    base_folder = "correctness_tests"
    orig_folder = "stressed_russian_texts"
    result_folder = "results_my_solution_old"

    base_path = f"{base_folder}/{orig_folder}"
    result_path = f"{base_folder}/{result_folder}"

    benchmark_everything_in_folder(base_path, result_path, ts.stress_text)


def perform_benchmark_for_russtress() -> None:
    stresser = Accent()
    base_folder = "correctness_tests"
    orig_folder = "stressed_russian_texts"
    result_folder = "results_russtress"

    base_path = f"{base_folder}/{orig_folder}"
    result_path = f"{base_folder}/{result_folder}"

    def stress_text(text: str) -> str:
        return stresser.put_stress(text).replace("'", "\u0301")

    benchmark_everything_in_folder(base_path, result_path, stress_text)


class RandomStresser:
    """Stresses texts randomly. Used for benchmarking."""

    def __init__(self) -> None:
        self._nlp = load_spacy_min()

    def stress_text(self, text: str) -> str:
        doc = self._nlp(text)
        final_text = ""
        for token in doc:
            final_text += self.stress_word_randomly(token.text) + token.whitespace_
        return final_text

    def stress_word_randomly(self, word: str) -> str:
        if has_only_one_syllable(word):
            return word
        else:
            # calculate the vowel indexes (аоэуыяеёюи)
            indexes = []
            for i, char in enumerate(word):
                if char.lower() in "аоэуыяеёюи":
                    indexes.append(i)
            if len(indexes) == 0:
                return word
            # choose a random vowel index
            stressed_index = random.choice(indexes)
            word_until_stressed = word[: stressed_index + 1]
            word_after_stressed = word[stressed_index + 1 :]
            # add the stress mark
            stressed_word = word_until_stressed + "\u0301" + word_after_stressed
            return stressed_word


def perform_benchmark_random():
    rs = RandomStresser()
    base_folder = "correctness_tests"
    orig_folder = "stressed_russian_texts"
    result_folder = "results_random"

    base_path = f"{base_folder}/{orig_folder}"
    result_path = f"{base_folder}/{result_folder}"

    benchmark_everything_in_folder(base_path, result_path, rs.stress_text)


def perform_benchmark_for_russ():
    model = StressPredictor()

    nlp = load_spacy_min()
    base_folder = "correctness_tests"
    orig_folder = "stressed_russian_texts"
    result_folder = "results_russ"

    base_path = f"{base_folder}/{orig_folder}"
    result_path = f"{base_folder}/{result_folder}"

    def stress_word(word: str):
        if has_only_one_syllable(word):
            return word
        else:
            stressed_index = model.predict(word)
            word_until_stressed = word[: stressed_index[-1] + 1]
            word_after_stressed = word[stressed_index[-1] + 1 :]
            # add the stress mark
            stressed_word = word_until_stressed + "\u0301" + word_after_stressed
            return stressed_word

    def stress_text(word: str) -> str:
        doc = nlp(word)
        final_text = ""
        for token in doc:
            final_text += stress_word(token.text) + token.whitespace_
        return final_text

    benchmark_everything_in_folder(base_path, result_path, stress_text)


def print_stressmistake_to_tsv(mistakes: list[StressMistake], tsv_path: str) -> None:
    """Prints a histogram of stress mistakes to a TSV file."""
    # The TSV will have the rows in the following order:
    # * The word
    # * The part of speech
    # * The morphological features
    # * The correct stress
    # * The incorrect stress
    # * The number of times the mistake was made

    with open(tsv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")

        mistakes_by_token = defaultdict(list)
        for mistake in mistakes:
            mistakes_by_token[
                (
                    mistake.orig_token,
                    mistake.unstressed_token_with_grammar_info.pos_,
                    mistake.auto_stressed_token,
                )
            ].append(mistake)

        # Sort the mistakes by the number of times they were made
        mistakes_by_token = sorted(
            mistakes_by_token.items(), key=lambda x: len(x[1]), reverse=True
        )

        writer.writerow(
            [
                "Word",
                "POS",
                "Auto-stressed word",
                "Example sentence" "Number of mistakes",
            ]
        )

        for (orig_token, pos, auto_stressed_token), mistakes in mistakes_by_token:
            # Print to the TSV
            writer.writerow(
                [
                    orig_token,
                    pos,
                    auto_stressed_token,
                    esc_nl(mistakes[0].unstressed_token_with_grammar_info.sent.text),
                    len(mistakes),
                ]
            )


def get_all_pos(
    stressed_text_path="correctness_tests/stressed_russian_texts",
) -> list[str]:
    """Gets all the POS tags in the corpus."""
    nlp = load_spacy_full()
    all_pos = set()
    for root, dirs, files in os.walk(stressed_text_path):
        for file in files:
            if file.endswith(".txt") or file.endswith(".ref"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    text = unaccentify(f.read())
                    doc = nlp(text)
                    for token in doc:
                        if not token_is_unimportant(token):
                            all_pos.add(token.pos_)
    return list(all_pos)


def print_benchmark_result_tsv():
    BASE_PATH = "correctness_tests"
    BENCHMARKED_SYSTEMS_PATHS: list[str] = [
        "results_reynolds",
        "results_my_solution",
        "results_russtress",
        "results_random",
        "results_russiangram_with_yo_fixed",
        "results_russ",
        "results_my_solution_old",
    ]
    ALL_POS = get_all_pos()

    ac = AccuracyCalculator()

    with open(
        f"{BASE_PATH}/benchmark_results.tsv", "w", encoding="utf-8", newline=""
    ) as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(
            [
                "System",
                "Percentage correct words",
                "Percentage unstressed words",
                "Percentage incorrect words",
                *["Correct: " + pos for pos in ALL_POS],
                *["Unstressed: " + pos for pos in ALL_POS],
                *["Incorrect: " + pos for pos in ALL_POS],
            ]
        )

        for benchmarked_system_path in BENCHMARKED_SYSTEMS_PATHS:
            # Get the name of the benchmarked system (delete results_ from the beginning)
            system_name = benchmarked_system_path[8:]
            # Get the statistics
            res = ac.calc_accuracy_over_dir(
                "correctness_tests/stressed_russian_texts",
                f"{BASE_PATH}/{benchmarked_system_path}",
            )
            total_result = sum(res, AnalysisResults.get_empty_results())

            cor = total_result.get_percentage_correctly_stressed_tokens()
            uns = total_result.get_percentage_unstressed_tokens()
            inc = total_result.get_percentage_incorrectly_stressed_tokens()

            # Sort the POS results by ALL_POS
            correct_pos_results = sorted(
                total_result.get_percentage_correctly_stressed_by_pos().items(),
                key=lambda x: ALL_POS.index(x[0]),
            )
            unstressed_pos_results = sorted(
                total_result.get_percentage_unstressed_by_pos().items(),
                key=lambda x: ALL_POS.index(x[0]),
            )
            incorrect_pos_results = sorted(
                total_result.get_percentage_incorrectly_stressed_by_pos().items(),
                key=lambda x: ALL_POS.index(x[0]),
            )

            # Print to the TSV
            writer.writerow(
                [
                    system_name,
                    cor,
                    uns,
                    inc,
                    *[x[1] for x in correct_pos_results],
                    *[x[1] for x in unstressed_pos_results],
                    *[x[1] for x in incorrect_pos_results],
                ]
            )


if __name__ == "__main__":
    #print(get_all_pos())
    #quit()
    # sp = StressPredictor()
    # res = sp.predict("ты")
    # print(res)
    #
    # quit()
    # print(RandomStresser().stress_text("когда"))
    # print(RandomStresser().stress_text("Привет, как дела?"))
    # quit()

    # print_benchmark_result_tsv()
    # quit()
    # perform_benchmark_for_russ()
    #
    # quit()
    #
    # perform_benchmark_random()
    perform_benchmark_for_my_solution_old()
    print_benchmark_result_tsv()

    # perform_benchmark_for_my_solution()

    # fix_russiangram_folder(
    #    "correctness_tests/results_russiangram_with_yo",
    #    "correctness_tests/results_russiangram_with_yo_fixed",
    # )

    # perform_benchmark_for_russtress()

    # print_statistics_over_data("correctness_tests/stressed_russian_texts")
    # quit()

    quit()