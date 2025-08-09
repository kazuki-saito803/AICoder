from langchain_ollama import ChatOllama


# Ollamaのモデル使用時に使用
def get_llm():
    return ChatOllama(model="gpt-oss:20b")
