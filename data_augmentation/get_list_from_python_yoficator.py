
with open("data_augmentation/yo.dat", "r", encoding="utf-8") as f:
    words: list[str] = []
    for line in f:
        split_by_base = line.split("(")
        if len(split_by_base) == 1:
            words.append(line.strip())
        else:
            word_base = split_by_base[0]
            suffixes = split_by_base[1].split("|")
            for suffix in suffixes:
                suffix = suffix.replace(")", "").strip()
                words.append(f"{word_base}{suffix}")

with open("data_augmentation/yo_expanded.txt", "w", encoding="utf-8") as out:
    out.write("\n".join(words))

