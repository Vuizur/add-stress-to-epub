import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

REPLACE_DICT = {
    "reynolds": "Reynolds",
    "russtress": "Russtress",
    "russtress_fixed": "Russtress-f",
    "random": "Random",
    "russiangram_with_yo_fixed": "RussianGram",
    "russ": "Russ",
    "tempdb_3_with_ruwikipedia": "Our system",
    "my_wsd": "Our system + WSD",
    "my_plus_russtress": "Our system + Russtress-f",
    "my_wsd_plus_russtress_fixed": "Our system + WSD + Russtress-f",
}


def rename_systems(df: pd.DataFrame) -> pd.DataFrame:

    df["System"] = df["System"].replace(REPLACE_DICT)
    return df


def create_correct_per_incorrect_column(df: pd.DataFrame) -> pd.DataFrame:
    df["Correct / incorrect"] = (
        df["Percentage correct words"] / df["Percentage incorrect words"]
    )
    return df


def plot_accuracy_all_systems():
    df = pd.read_csv("correctness_tests/benchmark_results.tsv", sep="\t")

    # Only keep the systems reynolds, russtress, random, russiangram_with_yo_fixed,
    # russ, tempdb_3_with_ruwikipedia
    df = df[
        df["System"].isin(
            [
                "reynolds",
                "russtress_fixed",
                "random",
                "russiangram_with_yo_fixed",
                "russ",
                "tempdb_3_with_ruwikipedia",
            ]
        )
    ]

    df = rename_systems(df)

    # Add a new column containing the quotient of the percentage of correct words and
    # the percentage of incorrect words
    df = create_correct_per_incorrect_column(df)

    # Sort the dataframe by the percentage of correct words
    df = df.sort_values(by="Percentage correct words", ascending=True)

    # Make the size of the font on the x-axis smaller
    plt.rcParams.update({"font.size": 9})

    sns.barplot(data=df, x="System", y="Percentage correct words")

    plt.savefig("correctness_tests/accuracy_all_systems.png", dpi=500)

    # Plot the percentage of unstressed words
    plt.clf()
    sns.barplot(data=df, x="System", y="Percentage unstressed words")
    plt.savefig("correctness_tests/unstressed_all_systems.png", dpi=500)

    # Plot the percentage of incorrect words
    plt.clf()
    sns.barplot(data=df, x="System", y="Percentage incorrect words")
    plt.savefig("correctness_tests/incorrect_all_systems.png", dpi=500)

    plt.clf()
    sns.barplot(data=df, x="System", y="Correct / incorrect")
    plt.savefig("correctness_tests/correct_incorrect_all_systems.png", dpi=500)


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(
        columns={
            "Percentage correct words": "% Correct",
            "Percentage unstressed words": "% Unstressed",
            "Percentage incorrect words": "% Incorrect",
        }
    )
    return df


def filter_relevant_columns_for_latex(df: pd.DataFrame) -> pd.DataFrame:
    stuff_to_potentially_filter = [
        "System",
        "Percentage correct words",
        "Percentage unstressed words",
        "Percentage incorrect words",
        "Correct / incorrect",
    ]
    stuff_to_potentially_filter = [
        x for x in stuff_to_potentially_filter if x in df.columns
    ]
    # Calculate intersection of the columns of the dataframe and the list of columns to
    # potentially filter, keeping order intact

    filtered = df[stuff_to_potentially_filter]
    # Rename the columns
    filtered = rename_columns(filtered)
    return filtered


def print_df_to_latex(df: pd.DataFrame) -> None:
    """Prints the dataframe to latex, keeping only 2 decimal places"""
    df = df.round(2)
    print(df.to_latex(index=False, escape=True, float_format="{:.2f}".format))


def plot_accuracy_my_systems():
    df = pd.read_csv("correctness_tests/benchmark_results.tsv", sep="\t")

    # Only keep the rows with the system columns
    # equal to tempdb_0_enwiktionary_only, tempdb_1_with_openrussian,
    # tempdb_2_with_ruwiktionary, tempdb_3_with_ruwikipedia

    df = df[
        df["System"].isin(
            [
                "tempdb_0_enwiktionary_only",
                "tempdb_1_with_openrussian",
                "tempdb_2_with_ruwiktionary",
                "tempdb_3_with_ruwikipedia",
            ]
        )
    ]

    # Rename the system names
    df["System"] = df["System"].replace(
        {
            "tempdb_0_enwiktionary_only": "EnWiktionary",
            "tempdb_1_with_openrussian": "EnWikt + OpenRussian",
            "tempdb_2_with_ruwiktionary": "EnWikt + OR + RuWiktionary",
            "tempdb_3_with_ruwikipedia": "EnWikt + OR + RuWikt + RuWiki",
        }
    )

    sns.set(style="whitegrid")

    bp = sns.barplot(
        data=df, x="System", y="Percentage correct words", hue="System", dodge=False
    )
    # bp.legend_.remove()
    bp.legend(loc="lower right")

    bp.set(xticklabels=[])
    plt.ylim(70, None)

    # Rotate x-axis labels

    plt.savefig("correctness_tests/accuracy_my_systems.png", dpi=400)
    plt.savefig("correctness_tests/accuracy_my_systems.svg")

    # Print to latex
    print(
        filter_relevant_columns_for_latex(df).to_latex(
            index=False, escape=True, float_format="{:.2f}".format
        )
    )

    # Now calculate the change of the percentage compared to the previous system
    # and print it to latex
    df["Diff correct"] = df["Percentage correct words"].diff()
    df["Diff correct"] = df["Diff correct"].fillna(0)
    df["Diff unstressed"] = df["Percentage unstressed words"].diff()
    df["Diff unstressed"] = df["Diff unstressed"].fillna(0)
    df["Diff incorrect"] = df["Percentage incorrect words"].diff()
    df["Diff incorrect"] = df["Diff incorrect"].fillna(0)

    # Print to latex
    diff_df = df[["System", "Diff correct", "Diff unstressed", "Diff incorrect"]]
    diff_df = diff_df.rename(
        columns={
            "Diff correct": "Δ % Correct",
            "Diff unstressed": "Δ % Unstressed",
            "Diff incorrect": "Δ % Incorrect",
        }
    )
    print_df_to_latex(diff_df)

    # Now divide the diff correct by the diff incorrect
    diff_df["Diff correct / incorrect"] = (
        diff_df["Δ % Correct"] / diff_df["Δ % Incorrect"]
    )
    print(diff_df)


def plot_chatgpt_minibenchmark():
    # load correctness_tests/chatgpt_minibenchmark.tsv
    df = pd.read_csv("correctness_tests/chatgpt_minibenchmark.tsv", sep="\t")

    # Rename System "My solution" to "Our solution"
    df["System"] = df["System"].replace({"My solution": "Our solution"})

    # Only keep systems Random, Our Solution, ChatGPT
    df = df[df["System"].isin(["Random", "Our solution", "ChatGPT"])]

    # Sort by percentage of correctly stressed tokens
    df = df.sort_values(by="Percentage of correctly stressed tokens", ascending=True)

    # Plot
    sns.barplot(
        data=df, x="System", y="Percentage of correctly stressed tokens"
    )  # , hue="System", dodge=False)
    plt.savefig("correctness_tests/accuracy_chatgpt.png", dpi=400)

    # Rename the columns
    df = df.rename(
        columns={
            "Percentage of correctly stressed tokens": "% Correct",
            "Percentage of incorrectly stressed tokens": "% Incorrect",
            "Percentage of unstressed tokens": "% Unstressed",
        }
    )
    # Keep only 2 decimal places
    df = df.round(2)
    print(df.to_latex(index=False, escape=True, float_format="{:.2f}".format))


def plot_fixing_russtress():
    # Load benchmark_results.tsv
    df = pd.read_csv("correctness_tests/benchmark_results.tsv", sep="\t")
    # Filter relevant columns for latex
    df = filter_relevant_columns_for_latex(df)
    # Keep only russtress and russtress_fixed
    df = df[df["System"].isin(["russtress", "russtress_fixed"])]
    # Rename russtress_fixed to russtress-fixed
    df["System"] = df["System"].replace(
        {"russtress": "Russtress", "russtress_fixed": "Russtress-fixed"}
    )
    df = df.round(2)
    print(df.to_latex(index=False, escape=True, float_format="{:.2f}".format))


def filter_relevant_pos_columns_and_add_correct_per_incorrect(
    df: pd.DataFrame, pos: str
) -> pd.DataFrame:
    """Filters the relevant columns for the given part of speech and adds a column with
    the quotient of correct and incorrect words"""
    df = df[
        [
            "System",
            f"Correct: {pos}",
            f"Unstressed: {pos}",
            f"Incorrect: {pos}",
        ]
    ]
    df = df.rename(
        columns={
            f"Correct: {pos}": "% Correct",
            f"Unstressed: {pos}": "% Unstressed",
            f"Incorrect: {pos}": "% Incorrect",
        }
    )
    df["Correct / incorrect"] = df["% Correct"] / df["% Incorrect"]
    return df


def filter_relevant_systems(df: pd.DataFrame) -> pd.DataFrame:
    # Only keep systems that are in REPLACE_DICT
    df = df[df["System"].isin(REPLACE_DICT.keys())]
    return df


def plot_really_all_systems():

    df = pd.read_csv("correctness_tests/benchmark_results.tsv", sep="\t")

    df = filter_relevant_systems(df)

    df = create_correct_per_incorrect_column(df)

    df = rename_systems(df)

    df = filter_relevant_columns_for_latex(df)

    df = rename_columns(df)

    # Keep only columns System, % Correct, % Unstressed, % Incorrect,
    # Correct / incorrect

    print(df)

    print_df_to_latex(df)


def plot_table_by_pos():
    # Plot tables for the parts of speech NOUN, VERB, ADJ, PROPN
    df = pd.read_csv("correctness_tests/benchmark_results.tsv", sep="\t")
    df = filter_relevant_systems(df)
    df = rename_systems(df)
    for pos in ["NOUN", "VERB", "ADJ", "PROPN"]:
        df_filtered = filter_relevant_pos_columns_and_add_correct_per_incorrect(df, pos)
        print(pos)
        # print(df_filtered)
        print_df_to_latex(df_filtered)


def plot_yofication_results():
    df = pd.read_csv("correctness_tests/benchmark_results.tsv", sep="\t")
    # Filter systems
    # tempdb_3_with_ruwikipedia_noyo, reynolds_noyo, russiangram_without_yo_fixed
    df = df[
        df["System"].isin(
            [
                "tempdb_3_with_ruwikipedia_noyo",
                "reynolds_noyo",
                "russiangram_without_yo_fixed",
            ]
        )
    ]

    # Rename systems
    df["System"] = df["System"].replace(
        {
            "tempdb_3_with_ruwikipedia_noyo": "Our system",
            "reynolds_noyo": "Reynolds",
            "russiangram_without_yo_fixed": "RussianGram",
        }
    )

    # Filter relevant columns
    df = create_correct_per_incorrect_column(df)
    df = filter_relevant_columns_for_latex(df)

    df = rename_columns(df)

    print_df_to_latex(df)
    # print(df)


if __name__ == "__main__":
    plot_yofication_results()
    # plot_table_by_pos()
    # plot_really_all_systems()
    # plot_accuracy_all_systems()
    # plot_accuracy_my_systems()
    # plot_chatgpt_minibenchmark()
    # plot_fixing_russtress()
