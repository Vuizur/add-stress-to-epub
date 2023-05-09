from dataclasses import dataclass
from stressed_cyrillic_tools import unaccentify
import csv

from russian_text_stresser.text_stresser import RussianTextStresser


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
                writer.writerow(
                    [
                        f"{esc_nl(token.text)}",
                        token.pos_,
                        esc_nl(doc2[i].text),
                        doc2[i].pos_,
                    ]
                )
            else:
                writer.writerow([esc_nl(token.text), token.pos_, "", ""])
        for i, token in enumerate(doc2):
            if i >= len(doc1):
                writer.writerow(["", "", esc_nl(token.text), token.pos_])

@dataclass
class StressOptions:
    canonical_form: str
    unstressed_form: str
    pos: str
    case_tags: list[str]
    form_of_word_id: int



def print_stressed_text_with_grammar_analysis(text: str):
    """Prints a sentence with stress and grammar analysis."""
    rts = RussianTextStresser()
    stressed_text = rts.stress_text(text)
    original_doc = rts._nlp(text)
    stressed_doc = rts._nlp(stressed_text)

    # enumerate through both docs in parallel
    for token, stressed_token in zip(original_doc, stressed_doc):
        stress_options = rts.rd._cur.execute("""
            SELECT w.word_id, w.pos, w.canonical_form, fow.form_of_word_id, ct.tag_text FROM word w 
            JOIN form_of_word fow ON w.word_id = fow.word_id 
            JOIN case_tags ct ON ct.form_of_word_id = fow.form_of_word_id
            WHERE w.word_lower_and_without_yo = ?
        """, (token.text.lower(),)).fetchall()

        stress_option_objs: list[StressOptions] = []
        # Convert to stress options
        for option in stress_options:
            # Check if form_of_word_id already exist. If yes, add tag
            for stress_option in stress_option_objs:
                if stress_option.form_of_word_id == option[3]:
                    stress_option.case_tags.append(option[4])
                    break
            else:
                stress_option_objs.append(
                    StressOptions(
                        canonical_form=option[2],
                        unstressed_form=token.text,
                        pos=option[1],
                        case_tags=[option[4]],
                        form_of_word_id=option[3],
                    )
                )

        print(
            f"{token.text} {token.pos_} {token.morph} # {stressed_token.text} //" + "|".join(
                f" {option.canonical_form} {option.pos} {option.case_tags}" for option in stress_option_objs
            )
        )


if __name__ == "__main__":
    text = "Тогда он сказал ей, что она ему понравилась ещё на первом курсе университета."
    text2 = "Вот видишь, – сказала она, – мне курить вредно, я уже падаю."
    text3 = "И если вдруг тебе казалось, что твоя сестра и её муж угадывали твои мысли, то такой приём называется «холодное чтение»."
    text4 = "Чем ближе к огороду, тем аллеи становились запущеннее, темнее и уже; на одной из них, прятавшейся в густой заросли диких груш, кислиц, молодых дубков, хмеля, целые облака мелких чёрных мошек окружили Ольгу Михайловну; она закрыла руками лицо и стала насильно воображать маленького человечка…"
    print_stressed_text_with_grammar_analysis(text4)