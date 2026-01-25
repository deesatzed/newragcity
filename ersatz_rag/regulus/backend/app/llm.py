import os

from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def call_llm(messages):

    response = await client.chat.completions.create(

        model="gpt-5",

        messages=messages,

        max_tokens=100000,

        temperature=0.6,

        top_p=0.95,

        logprobs=True,

        top_logprobs=20

    )

    return response
