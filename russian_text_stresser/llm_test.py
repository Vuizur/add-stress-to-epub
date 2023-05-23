from langchain.llms import LlamaCpp, HuggingFacePipeline
from langchain.prompts import PromptTemplate

WIZARDVICUNA7B_PROMPT = """### Instruction: {question}

### Response:""" # This is the prompt format recommended by .
WIZARD_VICUNA13B_PROMPT = "USER: {question}\nASSISTANT:" # This is the prompt format VicunaLM was trained on.
MANTICORE13B_PATH = r"D:\Programs\one-click-installers\text-generation-webui\models\Manticore-13B.ggmlv3.q4_0.bin"
WIZARD_VICUNA7B_PATH = r"D:\Programs\one-click-installers\text-generation-webui\models\Wizard-Vicuna-7B-Uncensored.ggmlv3.q4_1.bin"
MANTICORE_PROMPT = """### Instruction: {question}

### Assistant:"""

def test_cpp():
    llm = LlamaCpp(
        model_path=MANTICORE13B_PATH, 
    )
    request = MANTICORE_PROMPT.format(question="Write a short story about aliens!")
    print(llm(request))

if __name__ == "__main__":
    test_cpp()
