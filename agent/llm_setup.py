from langchain_ollama import ChatOllama
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from peft import PeftModel
from langchain_community.llms import HuggingFacePipeline


# Ollamaのモデル使用時に使用
def get_llm():
    return ChatOllama(model="phi3")

# Hugging Faceのモデル使用時に使用
def get_lora_fh_llm():
    base_model_name = "tiiuae/falcon-7b-instruct"
    lora_model_name = "yourname/falcon7b-lora-adapter"  # ← LoRA Weight

    # ベースモデル読み込み
    model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        device_map="auto"
    )
    tokenizer = AutoTokenizer.from_pretrained(base_model_name)

    # LoRA adapterを読み込んでマージ
    model = PeftModel.from_pretrained(model, lora_model_name)
    model = model.merge_and_unload()  # 推論高速化

    # HFのtext-generation pipelineに包む
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=128,
        temperature=0.7,
    )

    # LangChain側のラッパーを作って返す → ChatOllamaと同じように使える
    llm = HuggingFacePipeline(pipeline=pipe)
    return llm