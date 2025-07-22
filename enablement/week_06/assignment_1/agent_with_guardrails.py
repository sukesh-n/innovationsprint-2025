import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import tool, AgentExecutor, create_react_agent
from langchain import hub


from langfuse.langchain import CallbackHandler 
from nemoguardrails import LLMRails, RailsConfig


load_dotenv()

langfuse_handler = CallbackHandler()

print("--- Initialized LangFuse Handler ---")


@tool
def get_weather(city: str) -> str:
    """Gets the current weather for a given city. Returns a mock forecast."""
    print(f"--- Tool: get_weather called for {city} ---")
    if city.lower() == "london":
        return "The weather in London is sunny with a high of 22°C."
    elif city.lower() == "paris":
        return "Paris is currently cloudy with a chance of rain. Temperature is 18°C."
    else:
        return f"Sorry, I don't have weather information for {city}."

tools = [get_weather]


llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0)

prompt = hub.pull("hwchase17/react")

agent = create_react_agent(llm, tools, prompt)


agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    callbacks=[langfuse_handler] 
)

print("--- LangChain Agent Created ---")


config_path = "./guardrails_config/colang/"
config = RailsConfig.from_path(config_path)


rails = LLMRails(config, llm=llm)

rails.register_action(agent_executor, name="langchain_agent")

print("--- NeMo Guardrails Initialized and Agent Registered ---")


async def run_chat():
    print("\n--- Starting Interactive Chat (type 'exit' to quit) ---")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Bot: Goodbye!")
            break

        bot_response = await rails.generate_async(prompt=user_input)
        print(f"Bot: {bot_response}")


if __name__ == "__main__":
    import asyncio
    # To test the agent with Guardrails
    asyncio.run(run_chat())