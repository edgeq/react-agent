from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

response = client.responses.create(
    model="gpt-5.4-mini",
    input="Say hello in a formal 1890s manner. Treat me as if you were a vendor at the 1893 World's Fair in Chicago"
)

print(response.output_text)
