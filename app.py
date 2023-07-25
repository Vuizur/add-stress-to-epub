from litestar import Litestar, get
from russian_text_stresser.text_stresser import RussianTextStresser

stresser = RussianTextStresser()


@get("/stress_text/{text:str}")
async def stress_text(text: str) -> 0:
    return stresser.stress_text(text)

app = Litestar([stress_text])