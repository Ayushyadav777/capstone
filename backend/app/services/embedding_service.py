import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "text-embedding-3-small"


def create_embedding(text: str):

    response = client.embeddings.create(
        model=MODEL,
        input=text
    )

    answer = response.data[0].embedding


    # ✅ TOKEN TRACKING HERE
    usage = response.usage

    token_data = {
        "embedding_tokens": usage.total_tokens
    }

    return answer, usage.total_tokens   # 👈 return both