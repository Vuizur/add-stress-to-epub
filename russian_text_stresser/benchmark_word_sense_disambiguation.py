import csv
from dataclasses import dataclass
from collections.abc import Callable
import os
from russian_text_stresser.gpt3_WSD import (
    MANTICORE_13B,
    SAIGA_7B,
    WIZARD_L2_13B,
    WIZARD_VICUNA_7B,
    LocalLLM,
    find_correct_choice,
)
import re
from tqdm import tqdm
import random
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from russian_text_stresser.plot_accuracy import print_df_to_latex

@dataclass
class BenchmarkTask:
    complete_task: str
    correct_answer: int
    chatgpt_answer: int
    choices: list[str]


@dataclass
class BenchmarkResults:
    correct_answers: int = 0
    incorrect_answers: int = 0
    not_answered: int = 0

    def get_accuracy(self) -> float:
        """Return the accuracy in percent"""
        return (
            self.correct_answers
            / (self.correct_answers + self.incorrect_answers + self.not_answered)
            * 100
        )

    def __add__(self, other: "BenchmarkResults"):
        return BenchmarkResults(
            correct_answers=self.correct_answers + other.correct_answers,
            incorrect_answers=self.incorrect_answers + other.incorrect_answers,
            not_answered=self.not_answered + other.not_answered,
        )


def get_chatGPT_benchmark_results(
    benchmark_tasks: list[BenchmarkTask],
) -> BenchmarkResults:
    """Get the benchmark results for chatGPT"""
    bm_results = BenchmarkResults()
    for benchmark_task in benchmark_tasks:
        try:
            chatgpt_answer = int(benchmark_task.chatgpt_answer)
        except ValueError:
            bm_results.not_answered += 1

        if chatgpt_answer == benchmark_task.correct_answer:
            bm_results.correct_answers += 1
        else:
            bm_results.incorrect_answers += 1

    return bm_results


# Has the format:
"""
        Фраза: "Брат нам не писал."
Вопрос: Какое определение слова "писал" здесь правильное?
1. писа́ть (Глагол) - наносить на бумагу или иной материал графические знаки (буквы, цифры, ноты)
2. пи́сать (Глагол) - разг. испускать мочу; мочиться
3. писа́ло (Существительное) - палочка, которой писали на бересте
Ответ: (1)
CGPT: (1)


Фраза: "Скажи мне: Где здесь туалет? Я хочу писать."
Вопрос: Какое определение слова "писал" здесь правильное?
1. писа́ть (Глагол) - наносить на бумагу или иной материал графические знаки (буквы, цифры, ноты)
2. пи́сать (Глагол) - разг. испускать мочу; мочиться
Ответ: (2)
CGPT: (2)
"""


def load_chosen_tasks() -> list[BenchmarkTask]:
    with open("correctness_tests/wsd_test_dataset.txt", "r", encoding="utf-8") as f:
        text = f.read()

    tasks = text.split("\n\n")
    tasks = [task for task in tasks if "Фраза" in task]

    task_list: list[BenchmarkTask] = []

    # Loop through each task in the text file
    for task in tasks:
        stripped_task = task.strip()
        # Cut of everything behind Ответ:
        complete_task = stripped_task.split("Ответ:")[0]
        complete_task += "Отвечайте только цифрой."

        choices_line: str = re.search(r"\n1\..*\nОтвет", stripped_task, re.DOTALL).group(0).strip()  # type: ignore

        choices_lines = choices_line.split("\n")

        final_choices: list[str] = []
        for (
            line
        ) in (
            choices_lines
        ):  # This is needed because the choices can contain line breaks
            if re.match(r"^\d", line):
                final_choices.append(line)
            else:
                final_choices[-1] += line

        try:
            answer = re.search(r"\nОтвет: \((\d*\?*)\)", stripped_task).group(1)  # type: ignore
            answer = int(answer.replace("?", ""))
        except (AttributeError, ValueError):
            print(f"Could not find answer for task: {stripped_task}")
            continue

        chatgpt_answer = re.search(r"\nCGPT: \((\d*)\)", stripped_task).group(1)  # type: ignore

        chatgpt_answer = int(chatgpt_answer)

        # Create a dataclass object with the extracted information
        task_object = BenchmarkTask(
            complete_task, answer, chatgpt_answer, final_choices
        )

        # Append the object to the list
        task_list.append(task_object)

    # Print the list of dataclass objects
    return task_list


def benchmark_word_sense_disambiguation(
    answer_function: Callable[[str], str]
) -> BenchmarkResults:
    """Benchmark the word sense disambiguation task"""
    benchmark_tasks = load_chosen_tasks()
    bm_results = BenchmarkResults()
    for benchmark_task in tqdm(benchmark_tasks):
        try:
            llm_answer = answer_function(benchmark_task.complete_task)
            choice = find_correct_choice(llm_answer, benchmark_task.choices)
            if choice is not None:
                choice = int(choice.split(".")[0])
                if choice == benchmark_task.correct_answer:
                    bm_results.correct_answers += 1
                else:
                    bm_results.incorrect_answers += 1
            else:
                bm_results.not_answered += 1
        except Exception as e:
            print(f"Error while processing task: {benchmark_task.complete_task}")
            print(e)
            bm_results.not_answered += 1
    return bm_results


def print_benchmark_results_to_file(benchmark_results: BenchmarkResults, llm_name: str):
    # Print to tsv file
    with open(
        "correctness_tests/llm_benchmark_results.tsv", "a", encoding="utf-8", newline=""
    ) as f:
        # If empty, write the header
        if os.stat("correctness_tests/llm_benchmark_results.tsv").st_size == 0:
            writer = csv.writer(
                f, delimiter="\t", escapechar="\\", quoting=csv.QUOTE_NONE
            )
            writer.writerow(
                ["Name", "Correct", "Incorrect", "Not answered", "Percentage"]
            )

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


def print_results_to_png():
    # Read the data from the tsv file
    data = pd.read_csv("llm_benchmark_results.tsv", sep="\t")

    # Order the data by accuracy
    data = data.sort_values(by=["Percentage"], ascending=True)

    # Plot the histogram with seaborn
    sns.barplot(data=data, x="Name", y="Percentage")

    # Show the plot
    plt.savefig("results.png")


def choose_a_random_number(task: str) -> str:
    # Identify all numbers in the task
    numbers = re.findall(r"\d+\.", task)
    # Choose a random number from the list
    return random.choice(numbers)


def simulate_random_numbers_10000_times():
    bm = BenchmarkResults()
    for _ in range(10000):
        bm += benchmark_word_sense_disambiguation(choose_a_random_number)
    return bm


def perform_full_benchmark():
    SYSTEMS = [WIZARD_VICUNA_7B, MANTICORE_13B, SAIGA_7B, WIZARD_L2_13B]
    print_benchmark_results_to_file(simulate_random_numbers_10000_times(), "Random")
    for system in SYSTEMS:
        llm = LocalLLM(system)
        benchmark_results = benchmark_word_sense_disambiguation(llm.generate)
        print_benchmark_results_to_file(benchmark_results, llm.name)
    chatgpt_bm_results = get_chatGPT_benchmark_results(load_chosen_tasks())
    print_benchmark_results_to_file(chatgpt_bm_results, "ChatGPT")

def print_wsd_benchmark_result():
    df = pd.read_csv("correctness_tests/llm_benchmark_results.tsv", sep="\t")
    df = df.sort_values(by=["Percentage"], ascending=True)

    print(df)

    # Rename column Name to Model
    df = df.rename(columns={"Name": "Model"})
    # Rename model names
    df["Model"] = df["Model"].replace(
        {
            "wizard_vicuna_7B": "Wizard Vicuña 7B",
            "manticore_13B": "Manticore 13B",
            "saiga_7B": "Saiga 7B",
            "wizard_l2_13B": "Wizard Llama2 13B",
        }
    )
    # Only keep the model name and the percentage
    df = df[["Model", "Percentage"]]

    # Plot with seaborn
    bp = sns.barplot(data=df, x="Model", y="Percentage", hue="Model", dodge=False)

    bp.legend(loc="lower right")
    bp.set(xticklabels=[])

    # Show the plot
    plt.savefig("correctness_tests/results_wsd.png", dpi=400)

    # Print to latex
    print_df_to_latex(df)


if __name__ == "__main__":
    simulate_random_numbers_10000_times()
    quit()
    print(load_chosen_tasks())
    print_wsd_benchmark_result()
    # print(load_chosen_tasks())
    quit()

    # llama_2_13B = LocalLLM(WIZARD_VICUNA_7B)
    # benchmark_results = benchmark_word_sense_disambiguation(llama_2_13B.generate)
    # print_benchmark_results_to_file(benchmark_results, llama_2_13B.name)
    # simulate_random_numbers_10000_times()
    #perform_full_benchmark()

    #quit()
    # print_results_to_png()

    # quit()

    wizard_vicuna_7B = LocalLLM(WIZARD_VICUNA_7B)
    # manticore_13B = LocalLLM(MANTICORE_13B)
    # saiga_7B = LocalLLM(SAIGA_7B)

    # benchmark_results = benchmark_word_sense_disambiguation(manticore_13B.generate)
    # print_benchmark_results_to_file(benchmark_results, manticore_13B.name)
    # benchmark_results = benchmark_word_sense_disambiguation(saiga_7B.generate)
    # print_benchmark_results_to_file(benchmark_results, saiga_7B.name)

    # benchmark_results = benchmark_word_sense_disambiguation(
    #    lambda x: x, instead_return_chatgpt_results=True
    # )
    # print_benchmark_results_to_file(benchmark_results, "chatgpt")

    benchmark_results = benchmark_word_sense_disambiguation(wizard_vicuna_7B.generate)
    print_benchmark_results_to_file(benchmark_results, "wizard_vicuna_7B")

    # benchmark_results = simulate_random_numbers_10000_times()
    # print_benchmark_results_to_file(benchmark_results, "choose_a_random_number")
