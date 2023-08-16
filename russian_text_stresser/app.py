import uvicorn
from litestar import Litestar, post
from russian_text_stresser.text_stresser import RussianTextStresser
from litestar.config.cors import CORSConfig
from pydantic import BaseModel

cors_config = CORSConfig(allow_origins=["*"])

class StressRequest(BaseModel):
    text: str

stresser = RussianTextStresser()

@post("/stress_text/")
async def stress_text(data: StressRequest) -> str:
    return stresser.stress_text(data.text)

app = Litestar([stress_text], cors_config=cors_config)

if __name__ == "__main__":
    uvicorn.run(app)