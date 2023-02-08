from stressed_cyrillic_tools import unaccentify
import csv

def create_histogram_from_spacy_document(doc) -> dict[str, int]:
    """Creates a histogram of the words in a spacy document."""
    histogram = {}
    for token in doc:
        if token.text in histogram:
            histogram[unaccentify(token.text)] += 1
        else:
            histogram[unaccentify(token.text)] = 1
    return histogram

def diff_histograms(histogram1: dict[str, int], histogram2: dict[str, int]):
    """Returns a histogram of the differences between two histograms."""
    diff_histogram = {}
    for key in histogram1:
        if key in histogram2:
            diff_histogram[key] = histogram1[key] - histogram2[key]
        else:
            diff_histogram[key] = histogram1[key]
    for key in histogram2:
        if key not in histogram1:
            diff_histogram[key] = -histogram2[key]
    return diff_histogram

def print_spacy_doc_difference(doc1, doc2):
    """Prints the differences between two spacy documents."""
    histogram1 = create_histogram_from_spacy_document(doc1)
    histogram2 = create_histogram_from_spacy_document(doc2)
    diff_histogram = diff_histograms(histogram1, histogram2)
    print("Differences:")
    for key in diff_histogram:
        if diff_histogram[key] != 0:
            print("{}: {}".format(key, diff_histogram[key]))

def esc_nl(s: str):
    return s.replace("\r", "\\r").replace("\n", "\\n")

def print_two_docs_with_pos_next_to_another(doc1, doc2, filename="pos_comparison.tsv"):
    # This function iterates through two spacy documents
    # For each token it print <token> <pos> <token> <pos> to a tsv file

    # Open the file
    with open(filename, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t", escapechar="\\", quoting=csv.QUOTE_NONE)
        for i, token in enumerate(doc1):

            if i < len(doc2):
                writer.writerow([f"{esc_nl(token.text)}", token.pos_, esc_nl(doc2[i].text), doc2[i].pos_])
            else:
                writer.writerow([esc_nl(token.text), token.pos_, "", ""])
        for i, token in enumerate(doc2):
            if i >= len(doc1):
                writer.writerow(["", "", esc_nl(token.text), token.pos_])