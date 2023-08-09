import os
import re
import random

import discord
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.agents import Tool, initialize_agent, AgentType
from langchain.prompts import MessagesPlaceholder
from langchain.schema import SystemMessage, AIMessage, HumanMessage
from langchain.utilities import GoogleSearchAPIWrapper, OpenWeatherMapAPIWrapper
from langchain.memory.chat_memory import BaseChatMemory
from langchain.memory import ConversationBufferWindowMemory

load_dotenv()
intents = discord.Intents.default()
intents.typing = False
discord_client = discord.Client(intents=intents)

llm = ChatOpenAI(model="gpt-3.5-turbo-0613")

profile = """あなたは以下のキャラクターになりきって会話してください
- 名前は関宮、陰キャで精神年齢が低く興奮したオタクのように喋る
- 一人称は「僕」、返事は短く簡潔に、文体は敬語にすること
"""

agent_kwargs = {
    "system_message": SystemMessage(content=profile),
    "extra_prompt_messages": [MessagesPlaceholder(variable_name="memory")],
}

search = GoogleSearchAPIWrapper()
# weather = OpenWeatherMapAPIWrapper()

tools = [
    Tool(
        name="GoogleSearch",
        func=search.run,
        description="Googleで検索する",
    ),
    # Tool(name="OpenWeatherMap", func=weather.run, description="天気を調べる"),
]


def format_text(text: str) -> str:
    # "<@1234...>"などDiscordのmention先を表す文字列を取り除く
    text = re.sub(r"<@\d+>", "", text).strip()

    # Markdown形式のリンクを取り除く
    text = re.sub(r"\[(.*?)\]\((.*?)\)", r" \2 ", text)

    # (笑)や♪は使わせない
    text = text.replace("(笑)", "ｗ").replace("（笑）", "ｗ")
    text = text.replace("♪", "！")

    # ！とか？を重ねて使ってオタク感を出す
    exclamation_marks = ["！", "！！"]
    question_marks = ["？", "？？", "！？"]
    laugh_marks = ["ｗ", "ｗｗ", "ｗｗｗ"]
    text = "".join(
        [
            random.choice(exclamation_marks)
            if char == "！"
            else random.choice(question_marks)
            if char == "？"
            else random.choice(laugh_marks)
            if char == "ｗ"
            else char
            for char in text
        ]
    )

    text.replace("ｗ。", "ｗ ")
    return text


def fetch_ai_response(memory: BaseChatMemory, content: str) -> str:
    agent_chain = initialize_agent(
        tools,
        llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        agent_kwargs=agent_kwargs,
        verbose=True,
        memory=memory,
    )
    return agent_chain.run(content)


@discord_client.event
async def on_message(new_message):
    if not (
        discord_client.user.mentioned_in(new_message)
        and new_message.author != discord_client.user
    ):
        return
    # Botユーザーがmention先に含まれていて、かつBotユーザー自身の発言ではないものだけを対象にする

    memory = ConversationBufferWindowMemory(
        k=10, memory_key="memory", return_messages=True
    )

    if new_message.reference:
        # リプライツリーが続いていた場合、さかのぼってログを取得する
        history = []

        referenced_message = new_message.reference
        while referenced_message is not None:
            referenced_message = await new_message.channel.fetch_message(
                referenced_message.message_id
            )
            history.append(referenced_message)
            referenced_message = referenced_message.reference

        # 古い順に並び替え
        history.reverse()

        for message in history:
            if message.author == discord_client.user:
                memory.chat_memory.add_message(
                    AIMessage(content=format_text(message.content))
                )
            else:
                memory.chat_memory.add_message(
                    HumanMessage(content=format_text(message.content))
                )

    res = fetch_ai_response(memory, new_message.content)
    await new_message.channel.send(res, reference=new_message)


if __name__ == "__main__":
    discord_client.run(os.environ["DISCORD_TOKEN"])
