# coding=utf-8

import json
import pickle
import sqlite3

# from benchmark_accuracy import benchmark_accuracy
from stressed_cyrillic_tools import remove_accent_if_only_one_syllable, unaccentify
from text_stresser import RussianTextStresser
from ebook_dictionary_creator.e_dictionary_creator.dictionary_creator import (
    RussianDictionaryCreator,
)
from helper_methods import load_spacy_min, load_spacy_full


def find_hard_to_detect_case_words():
    # Idea: find all words where there are two or more prepositions
    # https://en.wikibooks.org/wiki/Russian/Prepositions
    # And then check if there are endings in adjectives/nouns that are identical in these cases (with stress/ё removed),
    # for example на копье́/на копьё
    # -> Implies a very high error rates
    # In the case of nouns, first check if there is an adjective that might help with identification of case
    # If not, then remove stress/return base word with changin it (maybe after checking error rate in real world)
    tagged_results = cur.execute(
        """
SELECT w.canonical_form, fow.form_of_word_id, tag_text
FROM word w 
JOIN form_of_word fow ON w.word_id = fow.word_id 
JOIN case_tags ct ON ct.form_of_word_id = fow.form_of_word_id
    """
    ).fetchall()

    # fow, (word, form_tags)
    fow_canonical_form_mapping: dict[int, str] = {}
    grouped_forms: dict[int, set] = {}
    for canonical_form, form_of_word_id, tag_text in tagged_results:
        fow_canonical_form_mapping[form_of_word_id] = canonical_form
        if form_of_word_id not in grouped_forms:
            grouped_forms[form_of_word_id] = {tag_text}
        else:
            grouped_forms[form_of_word_id].add(tag_text)

        fitting_word_candidates = set()
        for fow_key, tag_set in grouped_forms.items():
            if case in tag_set and plurality in tag_set:
                fitting_word_candidates.add(fow_canonical_form_mapping[fow_key])
        if len(fitting_word_candidates) == 1:
            return self.write_word_with_yo(word, fitting_word_candidates.pop())


# nlp = spacy.load('ru_core_news_sm')
# string = "Шарик улетел от Максима."
# string = "Он говорил о дворе"
# nlp.disable_pipes("ner")

# print(os.path.isfile("russian_dict.db"))
#


def test_json_dump():
    test_list = [
        "пространство, заросшее деревьями и другими растениями; бор, роща ◆ Роняет лес багряный свой убор.  А. С. Пушкин, «19 октября», 1825 г. [Викитека] ◆ Вот и лес. Тень и тишина. Статные осины высоко лепечут над вами; длинные, висячие ветки берёз едва шевелятся; могучий дуб стоит, как боец, подле красивой липы.  И. С. Тургенев, «Лес и степь (1848)», 1849 г. [Викитека] ◆ Однажды, в студёную зимнюю пору // Я и́з лесу вышел; был сильный мороз.  Н. А. Некрасов, «Крестьянские дети», 1861 г. [НКРЯ] ◆ Лесом частым и дремучим, // По тропинкам и по мхам, // Ехал всадник.  А. Н. Майков, «Кто он?», 1841 г., 1868 г.  ◆ У живописца Крамского есть одна замечательная картина под названием «Созерцатель»: изображён лес зимой, и в лесу, на дороге в оборванном кафтанишке и в лаптишках стоит один-одинёшенек, в глубочайшем уединении забредший мужичонко, стоит и как бы задумался, но он не думает, а что-то «созерцает».  Ф. М. Достоевский, «Братья Карамазовы», 1880 г. [НКРЯ]",
        "древесное сырьё на корню ◆ Валить лес ― работа тяжёлая, но здоровая. С рассвета до трёх-четырёх дня мы валили берёзы и ёлки, обрубали ветки, крыжевали стволы и таскали на плечах двухметровые поленья километра за полтора к реке.  Д. Самойлов, «Общий дневник», 1977–1989 г. [НКРЯ] ◆ Позже Урбанский рассказал мне, что в лагерях его отец, когда замерзали в бараке, поднял обессиленных, уже покорившихся людей, заставил в лютый мороз валить лес и тем спас их.  Г. Я. Бакланов, «Жизнь, подаренная дважды», 1999 г. [НКРЯ]",
        "неисч., собир., только ед. ч.: срубленные деревья; древесные материалы хозяйственного назначения ◆ Коростелёв увидел аккуратным штабелем сложенный лес ― материал для стройки, отборный материал, чистое сокровище.  В. Ф. Панова, «Ясный берег», 1949 г. [НКРЯ] ◆ Лишь в порту лебёдок визг обычный, // Новый деррик над углём кряхтит – // В трюмы пароходов заграничных // Грузят лес и камень-апатит.  А. В. Подстаницкий, «Мурманск вечером», 1940 // «Полярная правда»",
        "перен., собир., книжн., только ед. ч., с доп. чего?: множество каких-либо высоких, возвышающихся предметов ◆ Это был настоящий город из красного кирпича, с лесом высоко торчащих в воздухе закопчённых труб.  А. И. Куприн, «Молох», 1896 г. [НКРЯ] ◆ Лес штыков вырос в серой мгле рассвета перед изумлёнными казаками.  А. С. Серафимович, «Железный поток», 1924 г. [НКРЯ] ◆ Лес нефтяных вышек.  Юрий Черниченко, «Небесная глина (1968)», 1969 г. // «Юность» [НКРЯ] ◆ И сразу поднялся над партами лес рук, будто кавалерийский эскадрон выхватил сабли наголо.  Ю. И. Коваль, «Недопёсок», 1975 г. [НКРЯ] ◆ Перед лесом камер ― лес рук. Журналистская братия готова вытрясти из президента всё.  Борис Нисневич, «ЕГЭ для Путина (2003) // «Калининградская правда», 2003.06.10» [НКРЯ] ◆ Лес неподвижных людей  Ю. Кукин",
    ]

    # Insert test list int in memory sqliite db, encoded in json
    with sqlite3.connect(":memory:") as conn:
        conn.execute("CREATE TABLE words (json_ TEXT)")
        conn.execute(
            "INSERT INTO words (json_) VALUES (?)",
            (json.dumps(test_list, ensure_ascii=False),),
        )
        conn.commit()

        # Get data from db
        cursor = conn.execute("SELECT json_ FROM words")
        data = cursor.fetchone()[0]
        # decode json
        data = json.loads(data)
        # print data
        print(data)

def write_simple_cases():
    with open("simple_cases.pkl", "rb") as f:
        simple_cases = pickle.load(f)
    # Print to file
    with open("simple_cases.txt", "w", encoding="utf-8") as f:
        # Print dict
        for key, value in simple_cases.items():
            f.write(f"{key}: {value}\n")


if __name__ == "__main__":
    # Load simple_cases.pkl
    rd = RussianTextStresser()
    print(rd.stress_text("еж"))


    quit()
    nlp = load_spacy_full()
    for pipe in nlp.pipe_names:
        print(nlp.get_pipe_config(pipe))

    quit()
    str = "Пусти́те."
    nlp = load_spacy_min()
    doc = nlp(str)
    for token in doc:
        print(token.text, token.pos_, token.tag_, token.lemma_, token.is_stop)

    # for each char in str, print isalpha() and isdigit()
    # for char in str:
    #    print(char, char.isalpha(), char.isdigit())

    quit()
    test_json_dump()
    quit()
    yo_test1 = "Мое копье красивое."
    yo_test2 = "Это песня о копье."
    stress_test1 = "Твои слова ничего не значат."
    stress_test2 = "Почему не стоит говорить (и писать) фразу «от слова совсем»"

    test3 = "Больше всего на свете Джоэл хочет стать рифматистом."
    test4 = "Девушка вбежала в гостиную и остановилась, не зная, как поступить дальше. В углу тикали напольные часы, освещенные луной. В широком панорамном окне виднелись очертания раскинувшегося города: здания поднимались на десять этажей и выше, между ними протянулись линии пружинной дороги. Джеймстаун, ее дом все шестнадцать лет жизни."
    test5 = "Масляные капли, брызнув на расписную стену и дорогой ковер, заблестели в лунном свете."

    test6 = "Если они умирали в бою, то попадали туда сразу же."
    test7 = "Почему-то это не удалось."
    test8 = "Он пробил деревянные стены насквозь и продолжил полет, его шлем скрежетал о камни."
    # Bugged samer
    test9 = "Далинар грозной тенью замер в дверном проеме."
    test92 = "В дверном проеме, точно рубигончая, которую прогнали от теплого очага, замер Элокар."
    test93 = "Брат выглядит таким же, — добавил Гавилар, потирая бороду и изучая Тоха, который замер с напитком возле бара"
    test94 = "Адолин замер у перил, затерявшись в раздумьях."
    # Could not resolve ambiguity
    test10 = "Далинар в задумчивости потер подбородок."
    # bugged
    test11 = "Оно не двигалось — стояло с клинком на плече, с поднятым забралом, словно маленькая кукла."

    test11 = "Он стоил на большом стене"

    # ts = RussianTextStresser()
    # print(ts.stress_text(test7))
    # print(ts.stress_text("Ястреб"))
    # print(unaccentify("Я́стреб"))

    test_json = json.dumps(test_list, ensure_ascii=False)
    print(test_json)
    test_list = json.loads(test_json)
    print(test_list)

    quit()

    print(
        remove_accent_if_only_one_syllable(
            "Крикуны́ поко́рно вруча́ли свою́ судьбу́ в ру́ки Баргамо́та, протесту́я ли́шь для поря́дка."
        )
    )
    # benchmark_accuracy("correctness_tests/stressed_russian_texts/free/bargamot.txt")
    ts = RussianTextStresser()

    # print(ts.stress_text("Твои слова ничего не значат."))
    text1 = " рекоменду́я подда́ть жару́. Самого́ Баргамота"
    text2 = " рекоменду́я подда́ть жа́ру. Самого́ Баргамо́та"

    text100 = "Чехия предоставила Киеву военную помощь на 8,8 миллиарда рублей."

    test123 = "Это шутер от первого лица."

    print(ts.stress_text(test123))

    rdc = RussianDictionaryCreator(kaikki_file_path="russian-kaikki.json")
    rdc.export_kaikki_utf8("russian-kaikki-utf8.json")
