import csv
from dataclasses import dataclass
from collections.abc import Callable
from russian_text_stresser.gpt3_WSD import find_correct_choice
import re
from russian_text_stresser.llm_test import (
    WIZARD_VICUNA7B_PATH,
    WIZARDVICUNA7B_PROMPT,
    MANTICORE13B_PATH,
    MANTICORE_PROMPT,
    SAIGA7B_PATH,
    SAIGA7B_PROMPT,
)
from langchain.llms import LlamaCpp
from tqdm import tqdm
import random


@dataclass
class BenchmarkTask:
    complete_task: str
    correct_answer: int
    chatgpt_answer: str
    choices: list[str]


@dataclass
class BenchmarkResults:
    correct_answers: int = 0
    incorrect_answers: int = 0
    not_answered: int = 0

    def get_accuracy(self) -> float:
        """Return the accuracy in percent"""
        return (
            self.correct_answers / (self.correct_answers + self.incorrect_answers + self.not_answered) * 100
        )

    def __add__(self, other):
        return BenchmarkResults(
            correct_answers=self.correct_answers + other.correct_answers,
            incorrect_answers=self.incorrect_answers + other.incorrect_answers,
            not_answered=self.not_answered + other.not_answered,
        )


def benchmark_word_sense_disambiguation(
    answer_function: Callable[[str], str]
) -> BenchmarkResults:
    # Load the file "chosen_tasks.txt"
    with open("chosen_tasks.txt", "r", encoding="utf-8") as f:
        chosen_tasks = f.readlines()
        current_benchmark_task = ""
        bm_results = BenchmarkResults()

        writing_task = False
        # Iterate through lines until you find one that starts with "Фраза:"
        for line in tqdm(chosen_tasks):
            if line.startswith("Фраза:"):
                if current_benchmark_task != "":
                    # TODO: Refactor this to method
                    benchmark_task = BenchmarkTask(
                        complete_task=current_benchmark_task,
                        correct_answer=correct_answer,
                        choices=choices,
                        chatgpt_answer=cgpt_answer,
                    )
                    try:
                        llm_answer = answer_function(benchmark_task.complete_task)
                    except Exception as e:
                        print("Exception occurred:")
                        print(e)
                        print("For task:")
                        print(benchmark_task.complete_task)
                        llm_answer = ""
                    choice = find_correct_choice(llm_answer, benchmark_task.choices)
                    # Extract the number from the choice (e.g. "1." -> 1)
                    if choice is not None:
                        choice = int(choice.split(".")[0])
                        if choice == benchmark_task.correct_answer:
                            bm_results.correct_answers += 1
                        else:
                            bm_results.incorrect_answers += 1
                    else:
                        bm_results.not_answered += 1

                current_benchmark_task = ""
                choices: list[str] = []
                writing_task = True
            elif line.startswith("Ответ:"):
                current_benchmark_task += "Ответ:"
                writing_task = False
                correct_answer = (
                    line.split(":")[1]
                    .strip()
                    .replace("(", "")
                    .replace(")", "")
                    .replace("?", "")
                )  # Question mark sometimes answers I wanted to check again
                # Try to convert the correct answer to an int
                try:
                    correct_answer = int(correct_answer)
                except AttributeError:
                    print("Could not convert correct answer to int")
                    print(correct_answer)
                    print("For task:")
                    print(current_benchmark_task)
                    continue
                except ValueError:
                    print("Could not convert correct answer to int")
                    print(correct_answer)
                    print("For task:")
                    print(current_benchmark_task)
                    continue
                # print(current_benchmark_task)
            # Line starts with a number and dot
            elif re.match(r"^\d+\.", line):
                choices.append(line)
            elif line.startswith("CGPT:"):
                # Get the number from the line using regex. Anything before and after the number is ignored.
                cgpt_answer = re.search(r"\d+", line).group(0)
            if writing_task:
                current_benchmark_task += line

        # 1. све́дение (Существительное) - обычно мн. ч. известие, информация о чём-либо
        # 2. сведе́ние (Существительное) - уменьшение, сокращение, упрощение

        return bm_results


def print_benchmark_results_to_file(benchmark_results: BenchmarkResults, llm_name: str):
    # Print to tsv file
    with open("llm_benchmark_results.tsv", "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t", escapechar="\\", quoting=csv.QUOTE_NONE)
        writer.writerow(
            [
                llm_name,
                benchmark_results.correct_answers,
                benchmark_results.incorrect_answers,
                benchmark_results.not_answered,
                benchmark_results.get_accuracy(),
            ]
        )


# An enum for the different LLMs that also contains the path to the model and the prompt template
@dataclass
class LLM:
    name: str
    path: str
    prompt: str

WIZARD_VICUNA_7B = LLM(
    name="wizard_vicuna_7B",
    path=WIZARD_VICUNA7B_PATH,
    prompt=WIZARDVICUNA7B_PROMPT,
)

MANTICORE_13B = LLM(
    name="manticore_13B",
    path=MANTICORE13B_PATH,
    prompt=MANTICORE_PROMPT,
)

SAIGA_7B = LLM(
    name="saiga_7B",
    path=SAIGA7B_PATH,
    prompt=SAIGA7B_PROMPT,
)
    

class LocalLLM:
   def __init__(self, llm: LLM):
       self.llm = LlamaCpp(
           model_path=llm.path,
           temperature=0,
           n_ctx=1024, # Some tasks are too long for the default 512 context window
       )
       self.name = llm.name
       self.prompt = llm.prompt
   def generate(self, request: str) -> str:
       request = request.replace("Ответ:", "Отвечайте только цифрой.")
       print(request)
       return self.llm(self.prompt.format(question=request), )


if __name__ == "__main__":

    def always_first_in_dictionary(task: str) -> str:
        return "1."

    def always_second_in_dictionary(task: str) -> str:
        return "2."

    def always_third_in_dictionary(task: str) -> str:
        return "3."

    def choose_a_random_number(task: str) -> str:
        # Identify all numbers in the task
        numbers = re.findall(r"\d+\.", task)
    
        # Choose a random number from the list
        return random.choice(numbers)

    def simulate_random_numbers_10000_times():
        bm = BenchmarkResults()
        for i in range(10000):
            bm += benchmark_word_sense_disambiguation(choose_a_random_number)
        return bm

    #wizard_vicuna_7B = LlamaCpp(
    #    model_path=WIZARD_VICUNA7B_PATH,
    #)
    wizard_vicuna_7B = LocalLLM(WIZARD_VICUNA_7B)
    manticore_13B = LocalLLM(MANTICORE_13B)
    saiga_7B = LocalLLM(SAIGA_7B)

    #benchmark_results = benchmark_word_sense_disambiguation(manticore_13B.generate)
    #print_benchmark_results_to_file(benchmark_results, manticore_13B.name)

    benchmark_results = benchmark_word_sense_disambiguation(saiga_7B.generate)
    print_benchmark_results_to_file(benchmark_results, saiga_7B.name)

    #benchmark_results = benchmark_word_sense_disambiguation(wizard_vicuna_7B.generate)
    #print_benchmark_results_to_file(benchmark_results, "wizard_vicuna_7B")

    #benchmark_results = simulate_random_numbers_10000_times()
    #print_benchmark_results_to_file(benchmark_results, "choose_a_random_number")
