import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent


load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY").strip()

llm = ChatOpenAI(
    model="minimax/minimax-m2.5:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
    temperature=0.7,
)


async def main():
    server_params = StdioServerParameters(
        command="python3",
        args=["mcp_server.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await load_mcp_tools(session)
            print(f"✅ Loaded {len(tools)} tools: {[t.name for t in tools]}")

            agent = create_react_agent(llm, tools)

            print("✅ Smart Notepad Agent Ready!")
            print("Type 'exit' to quit\n")

            while True:
                user_input = input("You: ")

                if user_input.lower() == "exit":
                    print("Goodbye!")
                    break

                response = await agent.ainvoke(
                    {"messages": [{"role": "user", "content": user_input}]}
                )

                final_answer = response["messages"][-1].content
                print(f"Agent: {final_answer}\n")


if __name__ == "__main__":
    asyncio.run(main())