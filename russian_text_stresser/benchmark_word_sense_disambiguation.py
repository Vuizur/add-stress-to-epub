import csv
from dataclasses import dataclass
from collections.abc import Callable
from russian_text_stresser.gpt3_WSD import WIZARD_L2_13B, LocalLLM, find_correct_choice
import re
from tqdm import tqdm
import random
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
from llama_cpp import Llama


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
            self.correct_answers
            / (self.correct_answers + self.incorrect_answers + self.not_answered)
            * 100
        )

    def __add__(self, other):
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


def benchmark_word_sense_disambiguation(
    answer_function: Callable[[str], str], instead_return_chatgpt_results=False
) -> BenchmarkResults:
    # Load the file "chosen_tasks.txt"
    with open("chosen_tasks.txt", "r", encoding="utf-8") as f:
        chosen_tasks = f.readlines()
        current_benchmark_task = ""
        bm_results = BenchmarkResults()
        benchmark_tasks: list[BenchmarkTask] = []

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
                    benchmark_tasks.append(benchmark_task)

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

        if instead_return_chatgpt_results:
            return get_chatGPT_benchmark_results(benchmark_tasks)
        else:
            return bm_results


def print_benchmark_results_to_file(benchmark_results: BenchmarkResults, llm_name: str):
    # Print to tsv file
    with open(
        "correctness_tests/llm_benchmark_results.tsv", "a", encoding="utf-8", newline=""
    ) as f:
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


def stacked_barplot_example():
    # load dataset
    tips = sns.load_dataset("tips")

    # set plot style: grey grid in the background:
    sns.set(style="darkgrid")

    # set the figure size
    plt.figure(figsize=(14, 14))

    # top bar -> sum all values(smoker=No and smoker=Yes) to find y position of the bars
    total = tips.groupby("day")["total_bill"].sum().reset_index()

    # bar chart 1 -> top bars (group of 'smoker=No')
    bar1 = sns.barplot(x="day", y="total_bill", data=total, color="darkblue")

    # bottom bar ->  take only smoker=Yes values from the data
    smoker = tips[tips.smoker == "Yes"]

    # bar chart 2 -> bottom bars (group of 'smoker=Yes')
    bar2 = sns.barplot(
        x="day",
        y="total_bill",
        data=smoker,
        estimator=sum,
        errorbar=None,
        color="lightblue",
    )

    # add legend
    top_bar = mpatches.Patch(color="darkblue", label="smoker = No")
    bottom_bar = mpatches.Patch(color="lightblue", label="smoker = Yes")
    plt.legend(handles=[top_bar, bottom_bar])

    # show the graph
    plt.savefig("stacked_barplot_with_matplotlib_Python.svg")


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


if __name__ == "__main__":
    # stacked_barplot_example()

    llama_2_13B = LocalLLM(WIZARD_L2_13B)
    # print(llama_2_13B.generate("Пожалуйста, сочини историю про луны!"))
    benchmark_results = benchmark_word_sense_disambiguation(llama_2_13B.generate)
    print_benchmark_results_to_file(benchmark_results, llama_2_13B.name)

    quit()
    print_results_to_png()

    quit()

    # wizard_vicuna_7B = LlamaCpp(
    #    model_path=WIZARD_VICUNA7B_PATH,
    # )
    # wizard_vicuna_7B = LocalLLM(WIZARD_VICUNA_7B)
    # manticore_13B = LocalLLM(MANTICORE_13B)
    # saiga_7B = LocalLLM(SAIGA_7B)

    # benchmark_results = benchmark_word_sense_disambiguation(manticore_13B.generate)
    # print_benchmark_results_to_file(benchmark_results, manticore_13B.name)

    # benchmark_results = benchmark_word_sense_disambiguation(saiga_7B.generate)
    # print_benchmark_results_to_file(benchmark_results, saiga_7B.name)

    benchmark_results = benchmark_word_sense_disambiguation(
        lambda x: x, instead_return_chatgpt_results=True
    )
    print_benchmark_results_to_file(benchmark_results, "chatgpt")

    # benchmark_results = benchmark_word_sense_disambiguation(wizard_vicuna_7B.generate)
    # print_benchmark_results_to_file(benchmark_results, "wizard_vicuna_7B")

    # benchmark_results = simulate_random_numbers_10000_times()
    # print_benchmark_results_to_file(benchmark_results, "choose_a_random_number")
