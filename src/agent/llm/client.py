from agent.config import settings
from openai import OpenAI

client = OpenAI(api_key=settings.openai_api_key)

def get_response():
    response = client.responses.create(
        model=settings.model,
        input="Say hello in a formal 1890s manner. Treat me as if you were a vendor at the 1893 World's Fair in Chicago"
    )

    return response.output_text 