from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled, RunConfig
from openai import AsyncOpenAI
from decouple import config
import chainlit as cl
from openai.types.responses import ResponseTextDeltaEvent



set_tracing_disabled(True)

gemini_api_key = config("GEMINI_API_KEY")
gemini_base_url = config("GEMINI_BASE_URL")
gemini_model = config("GEMINI_MODEL_NAME")


gemini_client = AsyncOpenAI(api_key=gemini_api_key, base_url=gemini_base_url)
gemini_model = OpenAIChatCompletionsModel(openai_client=gemini_client, model=str(gemini_model))

English_agent = Agent(
    name="Abdul Mannan",
    instructions="you are english professor",
    model=gemini_model
)
                        
#prompt = input("Enter Your Question Here: ")
#result = Runner.run_sync(English_agent, prompt)
#print(result.final_output)


@cl.on_chat_start
async def handle_start_chat():
    cl.user_session.set("history" ,[])
    await cl.Message(content="Hello from Abdul Mannan").send()

@cl.on_message
async def handle_message(message: cl.Message):
    history = cl.user_session.get("history")

    msg = cl.Message(content="")
    await msg.send()

    history.append({"role": "user", "content":message.content})
    result = Runner.run_streamed(
        English_agent,
        input=history,
        run_config=RunConfig()
    )
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            await msg.stream_token(event.data.delta)
    history.append({"role": "assistant", "content": result.final_output})
    cl.user_session.set("history", history)
    # await cl.Message(content=result.final_output).send()