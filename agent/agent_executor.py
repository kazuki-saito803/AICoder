from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition, create_react_agent
from langchain_core.messages import SystemMessage
from .llm_setup import get_llm
from .llm_setup import get_hf_llm
from .tools import write_file, make_directory, git_init_and_push

def get_agent_executor():
    tools = [write_file, make_directory, git_init_and_push]
    llm = get_llm().bind_tools(tools)  # OllmaにするかHugging Faceにするかでここを変更

    system_message = SystemMessage(content=(
        "You are an autonomous coding agent. Your only way to take action is to call one of the provided tools. "
        "You MUST always call one of these tools to perform an action. Do not just explain; actually call them.\n\n"
        "Available tools: write_file(path: str, content: str), make_directory(input: str), git_init_and_push(input: str).\n"
        "Example:\n"
        "write_file(path='./hello.py', content='print(\"Hello\")')\n"
        "make_directory(input='{\"path\": \"./my_folder\"}')\n"
        "git_init_and_push(input='{\"repo_url\": \"https://github.com/xxx\", \"commit_msg\": \"first commit\", \"token\": \"ghp_xxx\"}')\n"
        "DO NOT explain. Only act using tool calls. You are not a chatbot, but an autonomous agent that performs tasks."
    ))

    # ノード構築は変更なし
    react_node = create_react_agent(llm, tools)

    builder = StateGraph(dict)
    builder.add_node("agent", react_node)
    builder.add_node("tools", ToolNode(tools))

    builder.set_entry_point("agent")
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools", "agent")
    builder.add_edge("agent", END)

    graph = builder.compile()
    return graph, system_message