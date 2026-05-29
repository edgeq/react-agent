from agent.config import settings
from openai import OpenAI

client = OpenAI(api_key=settings.openai_api_key)

def get_response(user_prompt: str):
    response = client.responses.create(
        model=settings.model,
        input=user_prompt
    )

    return response.output_text 

def get_chat_response(messages: list[dict], tools: list[dict] | None = None):
    kwargs = {
        "model": settings.model,
        "input": messages
    }
    if tools:
        kwargs["tools"] = tools

    return client.responses.create(**kwargs)
