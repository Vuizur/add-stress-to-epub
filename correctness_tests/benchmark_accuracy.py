
from helper_methods import remove_accent_if_only_one_syllable
from text_stresser import RussianTextStresser
from correctness_tests.remove_accented_chars import remove_accented_chars

def benchmark_accuracy(file_path: str):
    stresser = RussianTextStresser()
    with open(file_path, "r", encoding="utf-8") as file:
        text_file = file.read()
        text_file = remove_accent_if_only_one_syllable(text_file)
        text_file_unstressed = remove_accented_chars(text_file)
        split_file_as_it_should_be = text_file.split(" ")
        stressed_file = stresser.stress_text(text_file_unstressed)
        split_file_by_my_program = stressed_file.split(" ")
    correct_tokens = 0
    wrong_tokens = 0
    for i in range(0, len(split_file_as_it_should_be)):
        #The stress of one-syllable words is obvious and usually not marked
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
    with open(f"correctness_tests/results/{file_name_stump}_original.txt", "w", encoding="utf-8") as orig, \
        open(f"correctness_tests/results/{file_name_stump}_edit.txt", "w", encoding="utf-8") as edit:
        orig.write(text_file)
        edit.write(stressed_file)



