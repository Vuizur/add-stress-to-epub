import unittest
from russian_dictionary import RussianDictionary
from text_stresser import RussianTextStresser


class StressTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.rd = RussianDictionary("russian_dict.db")
        self.stresser = RussianTextStresser()

    def test_simple_case(self):
        self.assertEqual(self.rd.get_stressed_word_and_set_yo("тупо"), "ту́по")

    def test_uppercase_simple_case(self):
        self.assertEqual(self.rd.get_stressed_word_and_set_yo("Огромный"), "Огро́мный")

    def test_ambiguous_case(self):
        self.assertEqual(self.rd.get_stressed_word_and_set_yo("головы"), "головы")

    def test_upper_ambiguous_case(self):
        self.assertEqual(self.rd.get_stressed_word_and_set_yo("Потом"), "Потом")

    def test_yo(self):
        self.assertEqual(self.rd.get_stressed_word_and_set_yo("еж"), "ёж")

    def test_ambiguous_yo_case(self):
        self.assertEqual(self.rd.get_stressed_word_and_set_yo("копье"), "копье")

    def test_uppercase_yo(self):
        self.assertEqual(self.rd.get_stressed_word_and_set_yo("Зеленый"), "Зелёный")

    def test_uppercase_ambiguous_yo_case(self):
        self.assertEqual(self.rd.get_stressed_word_and_set_yo("Копье"), "Копье")

    def test_genitive(self):
        self.assertEqual(self.stresser.stress_text("Лица сияют."), "Ли́ца сия́ют.")

    # Test "Э́то шу́тер от первого лица́.""
    def test_sentence_plural(self):
        self.assertEqual(
            self.stresser.stress_text("Это шутер от первого лица."),
            "Э́то шу́тер от первого лица́.",
        )

    def test_sentence_one_syllable(self):
        self.assertEqual(
            self.stresser.stress_text("Эти красивые леса!"), "Э́ти краси́вые леса́!"
        )

    def test_sentence_genitive(self):
        self.assertEqual(
            self.stresser.stress_text("Это магия этого леса."),
            "Э́то ма́гия э́того ле́са.",
        )

    def test_bylo(self):
        self.assertEqual(
            self.stresser.stress_text("Это было давно."), "Э́то бы́ло давно́."
        )

    # SO FAR FAILING TESTS
    def test_vselennaya(self):
        self.assertEqual(
            self.stresser.stress_text(
                "В конце концов, небольшое сумасшествие гораздо, гораздо более вероятно, чем вселенная, содержащая в себе магию."
            ),
            "В конце́ концо́в, небольшо́е сумасше́ствие гора́здо, гора́здо бо́лее вероя́тно, чем вселе́нная, содержа́щая в себе́ ма́гию.",
        )


# Но е́сли ничего́ не произойдёт, то ты признаешь, что ошиба́лась.

# Она́ вста́ла, подошла́ к за́пертой две́ри и взмахну́ла па́лочкой. Вокру́г неё появи́лась расплы́вчатая завеса, непроница́емая для зре́ния и слу́ха, кото́рая че́рез не́сколько мину́т пропа́ла

# кото́рые с отча́яньем и стра́хом сгрудились в ку́чу и, не зна́я, что предприня́ть, взира́ли на пятеры́х старшеку́рсников

# Профе́ссор закати́л глаза

if __name__ == "__main__":
    unittest.main()
