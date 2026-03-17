import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def rerank(query, papers):

    prompt = f"""
Rank these papers by relevance.

Query:
{query}

Papers:
{papers}

Return ranked list.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return papers