from ollama import chat


MODEL_NAME = "qwen2.5:7b"
def ask_llm(prompt:str)->str:
    response = chat(
        model = MODEL_NAME,
        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ]
    )
    return response.message.content