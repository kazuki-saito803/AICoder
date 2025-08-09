import click
from langchain_core.messages import HumanMessage, SystemMessage
from agent.agent_executor import get_agent_executor

@click.group()
def cli():
    pass

@cli.command()
def start():
    print("AICoderへようこそ！やりたいことを入力してください：\n")
    instruction = input("> ")

    graph, system_message = get_agent_executor()

    print("\n実行中...\n")
    for step in graph.stream({"messages": [system_message, HumanMessage(content=instruction)]}):
        if "agent" in step:
            agent_data = step["agent"]
            # agent_data がリストなら最後のcontentを取る、安全にcontentを取得
            if isinstance(agent_data, list) and len(agent_data) > 0:
                content = agent_data[-1].content
            else:
                content = getattr(agent_data, "content", str(agent_data))
            print(f"[Agent Thought] {content}")

        if "tools" in step:
            print(f"[Tool Result] {step['tools']}")

    print("\n完了しました！")

if __name__ == "__main__":
    cli()
