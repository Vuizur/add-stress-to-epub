# coding=utf-8
import sqlite3
import spacy
import os

from russian_dictionary import RussianDictionary

#con = sqlite3.connect("russian_dict.db.")
#cur = con.cursor()

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


nlp = spacy.load('ru_core_news_sm')
#string = "Шарик улетел от Максима."
#string = "Он говорил о дворе"
#nlp.disable_pipes("ner")

print(os.path.isfile("russian_dict.db"))

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

doc = nlp(test10)
#spacy.displacy.serve(doc, style='dep')
rd = RussianDictionary()

for token in doc:
    print(token.text)
    print(token.pos_)
    print(token.morph.to_dict())
    print(rd.get_stressed_word_and_set_yo(token.text, token.pos_, token.morph))