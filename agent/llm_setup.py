from langchain_ollama import ChatOllama

def get_llm():
    return ChatOllama(model="qwen2.5-coder")
