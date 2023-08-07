#from langchain.llms import LlamaCpp, HuggingFacePipeline
#from langchain.prompts import PromptTemplate

WIZARDVICUNA7B_PROMPT = """### Instruction: {question}

### Response:""" # This is the prompt format recommended by .
WIZARD_VICUNA13B_PROMPT = "USER: {question}\nASSISTANT:" # This is the prompt format VicunaLM was trained on.
MANTICORE13B_PATH = r"D:\Programs\one-click-installers\text-generation-webui\models\Manticore-13B.ggmlv3.q4_0.bin"
WIZARD_VICUNA7B_PATH = r"D:\Programs\one-click-installers\text-generation-webui\models\Wizard-Vicuna-7B-Uncensored.ggmlv3.q4_1.bin"
MANTICORE_PROMPT = """### Instruction: {question}

### Assistant:"""

SAIGA7B_PATH = r"D:\Programs\one-click-installers\text-generation-webui\models\saiga--7b-ggmlv3-model-q4_1.bin"
SAIGA7B_PROMPT = """
Ты — Сайга, русскоязычный автоматический ассистент. Ты разговариваешь с людьми и помогаешь им.
User: {question}
Saiga: """

def test_cpp():
    from llama_cpp import Llama

    llm = Llama(
        model_path=MANTICORE13B_PATH, 
        n_ctx=2048,
    )
    request = MANTICORE_PROMPT.format(question="Write a cool short story.")
    print(llm(request))

def test_saiga():
    from llama_cpp import Llama

    llm = Llama(
        model_path=SAIGA7B_PATH,
    )
    request = SAIGA7B_PROMPT.format(question="Пожалуйста, сочини историю про луны!")
    print(llm(request))

if __name__ == "__main__":
    test_cpp()
