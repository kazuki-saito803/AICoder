from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition, create_react_agent
from langchain_core.messages import SystemMessage

from .llm_setup import get_llm
from .tools import write_file, make_directory, git_init_and_push

def safe_tools_condition(state):
    # 元のtools_conditionを利用
    decision = tools_condition(state)
    # 状態にLLMの最後の応答を含むキーを使って 'TERMINATE' の有無を判定
    last_output = state.get("last_llm_output", "")
    if "TERMINATE" in last_output:
        return END
    return decision

def get_agent_executor():
    tools = [write_file, make_directory, git_init_and_push]
    llm = get_llm().bind_tools(tools)

    system_message = SystemMessage(content=(
        "You are an autonomous coding agent. Your only way to take action is to call one of the provided tools. "
        "You MUST always call one of these tools to perform an action. Do not just explain; actually call them.\n\n"
        "Available tools: write_file(path: str, content: str), make_directory(input: str), git_init_and_push(input: str).\n"
        "Example:\n"
        "write_file(path='./hello.py', content='print(\"Hello\")')\n"
        "make_directory(input='{\"path\": \"./my_folder\"}')\n"
        "git_init_and_push(input='{\"repo_url\": \"https://github.com/xxx\", \"commit_msg\": \"first commit\", \"token\": \"ghp_xxx\"}')\n"
        "If you have completed all your tasks, respond with the single word 'TERMINATE' and do not call any more tools.\n"
        "DO NOT explain. Only act using tool calls. You are not a chatbot, but an autonomous agent that performs tasks."
    ))

    react_node = create_react_agent(llm, tools)

    builder = StateGraph(dict)
    builder.add_node("agent", react_node)
    builder.add_node("tools", ToolNode(tools))

    builder.set_entry_point("agent")
    builder.add_conditional_edges("agent", safe_tools_condition)
    builder.add_edge("tools", "agent")
    builder.add_edge("agent", END)

    graph = builder.compile()
    return graph, system_message