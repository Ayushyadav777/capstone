import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "text-embedding-3-small"


def create_embedding(text: str):

    response = client.embeddings.create(
        model=MODEL,
        input=text
    )

    return response.data[0].embedding