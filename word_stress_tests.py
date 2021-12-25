import unittest
from russian_dictionary import RussianDictionary

class StressTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.rd = RussianDictionary()

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


if __name__ == '__main__':
    unittest.main()