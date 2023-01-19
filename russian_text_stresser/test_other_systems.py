from russtress import Accent

def test_russtress():
    accent = Accent()
    text = 'Проставь, пожалуйста, ударения'
    accented_text = accent.put_stress(text)
    print(accented_text)


if __name__ == "__main__":
    accentor = Accentor()