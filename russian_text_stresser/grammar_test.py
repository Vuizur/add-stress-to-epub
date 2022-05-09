# coding=utf-8

from benchmark_accuracy import benchmark_accuracy
from helper_methods import remove_accent_if_only_one_syllable, unaccentify
from text_stresser import RussianTextStresser

def find_hard_to_detect_case_words():
    # Idea: find all words where there are two or more prepositions 
    # https://en.wikibooks.org/wiki/Russian/Prepositions
    # And then check if there are endings in adjectives/nouns that are identical in these cases (with stress/ё removed),
    # for example на копье́/на копьё
    # -> Implies a very high error rates
    # In the case of nouns, first check if there is an adjective that might help with identification of case
    # If not, then remove stress/return base word with changin it (maybe after checking error rate in real world)
    tagged_results = cur.execute("""
SELECT w.canonical_form, fow.form_of_word_id, tag_text
FROM word w 
JOIN form_of_word fow ON w.word_id = fow.word_id 
JOIN case_tags ct ON ct.form_of_word_id = fow.form_of_word_id
    """).fetchall()
    
    #fow, (word, form_tags)
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


#nlp = spacy.load('ru_core_news_sm')
#string = "Шарик улетел от Максима."
#string = "Он говорил о дворе"
#nlp.disable_pipes("ner")

#print(os.path.isfile("russian_dict.db"))
if __name__ == "__main__":
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
    #Bugged samer
    test9 = "Далинар грозной тенью замер в дверном проеме."
    test92 = "В дверном проеме, точно рубигончая, которую прогнали от теплого очага, замер Элокар."
    test93 = "Брат выглядит таким же, — добавил Гавилар, потирая бороду и изучая Тоха, который замер с напитком возле бара"
    test94 = "Адолин замер у перил, затерявшись в раздумьях."
    #Could not resolve ambiguity
    test10 = "Далинар в задумчивости потер подбородок."
    #bugged
    test11 = "Оно не двигалось — стояло с клинком на плече, с поднятым забралом, словно маленькая кукла."

    test11 = "Он стоил на большом стене"

    #ts = RussianTextStresser()
    #print(ts.stress_text(test7))
    #print(ts.stress_text("Ястреб"))
    #print(unaccentify("Я́стреб"))

    print(remove_accent_if_only_one_syllable("Крикуны́ поко́рно вруча́ли свою́ судьбу́ в ру́ки Баргамо́та, протесту́я ли́шь для поря́дка."))
    #benchmark_accuracy("correctness_tests/stressed_russian_texts/free/bargamot.txt")
    ts = RussianTextStresser()
    text100 = "Прика́зчики ло́вят Гараську и бьют, — толпа́ хохо́чет, рекоменду́я подда́ть жару́. Самого́ Баргамота Гараська руга́л так фантасти́чески реа́льно, что тот, не понима́я да́же всей со́ли Гараськиных остро́т, чу́вствовал, что он оби́жен бо́лее, чем е́сли бы его́ вы́пороли. Чем промышля́л Гараська, остава́лось для пушкаре́й одно́й из тайн, кото́рыми бы́ло облечено́ всё его́ существова́ние. Тре́звым его́ не ви́дел никто́, да́же та ня́нька, кото́рая в де́тстве ушиба́ет ребя́т, по́сле чего́ от них слы́шится спиртный запах, — от Гараськи и до уши́ба несло́ сиву́хой. Жил, то есть ночева́л, Гараська по огоро́дам, по бе́регу, под кусточками. Зимо́й куда́-то исчеза́л, с пе́рвым дыха́нием весны́ появля́лся. Что его́ привлека́ло на Пушкарную, где его́ не бил то́лько лени́вый, — бы́ло опя́ть-таки та́йной бездо́нной Гараськиной души́, но вы́жить его́ ниче́м не могли́. Предполага́ли, и не без основа́ния, что Гараська поворо́вывает, но пойма́ть его́ не могли́ и би́ли лишь на основа́нии ко́свенных ули́к."

    tok_exp = ts.nlp.tokenizer.explain(text100)
    for t in tok_exp:
        print(t[1], "\t", t[0])

