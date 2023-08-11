# Import the scipy library for statistical functions
import scipy.stats as stats
import pandas

def calculate_statistical_significance(n1: int, n2: int, c1: int, c2: int, alternative_hypothesis: str="greater"):
    """
    Calculates the statistical significance of the difference in accuracy between two programs.
    
    Parameters
    ----------
    n1 : int
        The sample size (number of cases) for program 1.
    n2 : int
        The sample size (number of cases) for program 2.
    c1 : int
        The number of correct classifications for program 1.
    c2 : int
        The number of correct classifications for program 2.
    
    Returns
    -------
    p_value : float
        The p-value of the binomial test.
    """
    # Calculate the proportion of correct classifications for each program
    p1 = c1 / n1 # Program 1
    # p2 = c2 / n2 # Program 2

    # Perform the binomial test using the binom_test function
    # Choose program 1 as the reference program
    p_value = stats.binom_test(x=c2, n=n2, p=p1, alternative=alternative_hypothesis)

    # Return the p-value
    return p_value

if __name__ == "__main__":
    TOTAL_TOKENS = 22665

    # Test the function
    # Load correctness_tests/benchmark_results.tsv
    with open("correctness_tests/benchmark_results.tsv", "r", encoding="utf-8") as f:
        # Read the file
        data = pandas.read_csv(f, sep="\t")

        # Find the row where the System column is equal to tempdb_3_with_ruwikipedia
        our_program_row = data.loc[data["System"] == "tempdb_3_with_ruwikipedia"]

        # Now get the column "Number of correct words"
        our_program_correct_words = our_program_row["Number of correct words"].values[0]
        print("Our program correct words:", our_program_correct_words)

        # Now we iterate over all the rows and calculate the p-value for each program
        
        for index, row in data.iterrows():
            # Get the program name
            program_name = row["System"]
            
            if program_name == "tempdb_3_with_ruwikipedia":
                continue

            # Get the number of correct words
            correct_words = row["Number of correct words"]

            # Calculate the p-value
            p_value = calculate_statistical_significance(n1=TOTAL_TOKENS, n2=TOTAL_TOKENS, c1=correct_words, c2=our_program_correct_words)

            # Print the program name and the p-value
            print(program_name, p_value)

        # Now we do the same, but with the column "Number of incorrect words"
        print("\n\n\n")
        our_program_incorrect_words = our_program_row["Number of incorrect words"].values[0]

        for index, row in data.iterrows():
            # Get the program name
            program_name = row["System"]
            
            if program_name == "tempdb_3_with_ruwikipedia":
                continue

            # Get the number of incorrect words
            incorrect_words = row["Number of incorrect words"]

            # Calculate the p-value
            p_value = calculate_statistical_significance(n1=TOTAL_TOKENS, n2=TOTAL_TOKENS, c1=incorrect_words, c2=our_program_incorrect_words, alternative_hypothesis="less")

            # Print the program name and the p-value
            print(program_name, p_value)

