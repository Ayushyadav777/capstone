import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def extract_search_phrase(query: str):

    prompt = f"""
Extract the core biomedical search phrase from the query.

Rules:
- Return only ONE phrase
- No explanation
- Maximum 4-6 words
- Must represent the main medical topic

Examples:

Query: What are the latest treatment options for pancreatic cancer?
Answer: pancreatic cancer treatment

Query: New therapies for Alzheimer's disease
Answer: alzheimer disease therapy

Query: risk factors of lung cancer
Answer: lung cancer risk factors

Query:
{query}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()