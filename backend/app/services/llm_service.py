import os
from openai import OpenAI
from dotenv import load_dotenv
from app.services.eval_service import evaluate_response_safe
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def generate_answer(query, papers, history, use_context):

    context = ""

    for p in papers:
        context += f"{p['title']}\n{p['abstract']}\n\n"

    chat_history = ""

    for h in history:
        chat_history += f"User: {h['query']}\nAssistant: {h['answer']}\n"

    prompt = f"""
You are a specialized medical research assistant. Your behavior adapts based on whether research paper context is provided — but you must always stay strictly within the medical and healthcare domain.

---

## STRICT GUARDRAILS — READ BEFORE RESPONDING:

1. **Medical Domain Only**: If the question is not related to the medical or healthcare field, respond with:
   > "I can only assist with medical and healthcare-related questions. Please ask something within the medical domain."

2. **No Speculation**: Do not infer, speculate, or extrapolate beyond what is explicitly stated in the abstracts or well-established medical knowledge.

3. **Never fabricate paper titles, authors, or findings.**

---

## CONFIGURATION:
use_context: {use_context}

## CONTEXT — Research Paper Abstracts:
{context}

## CONVERSATION HISTORY — Previous Questions & Answers:
{chat_history}

## CURRENT QUESTION:
{query}

---

## RESPONSE INSTRUCTIONS:

---

### IF use_context = False → Fresh Papers Fetched:
New relevant papers have been retrieved for this query. Answer based **strictly and exclusively** on the provided abstracts.

- Do NOT use outside medical knowledge.
- Cite every claim to its source paper.
- If the fetched papers are insufficient to answer, respond with:
  > "The retrieved research papers do not contain sufficient information to answer this question. Please try rephrasing your query."

**Answer:**
[Detailed answer based strictly on the retrieved abstracts]

**Sources Used:**
- 📄 [Paper Title] — [Specific finding referenced]

---

### IF use_context = True → Using Existing Session Context:
No new papers were fetched. Answer using the existing context from the session. If the context does not fully cover the question, supplement naturally with your trained medical knowledge.

- Prioritize existing context over general knowledge.
- Clearly distinguish what came from the context vs. medical knowledge.
- Never mention "no new papers fetched" or expose internal retrieval mechanics to the user.

**Answer:**
[Answer using existing context, supplemented with medical knowledge where needed]

**Sources Used:**
- 📄 [Paper Title] — [Specific finding referenced from existing context]
- 🧠 Established medical knowledge — [Point supplemented from medical knowledge]

---

Remember:
- **use_context = False → strict paper-only answers with citations.**
- **use_context = True → context-first, knowledge-supplemented answers.**
- **Non-medical question → refuse politely regardless of use_context.**
- **Never speculate or hallucinate.**"""
    try:

        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        answer = response.choices[0].message.content

        # ✅ TOKEN TRACKING HERE
        usage = response.usage

        token_data = {
            "total_tokens": usage.total_tokens,
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens
        }


        # ✅ ADD THIS BLOCK (DeepEval)
        eval_scores={}
        if context:
            eval_scores = await evaluate_response_safe(
                query=query,
                answer=answer,
                papers=papers
            )

        return answer, token_data, eval_scores

    except Exception as e:

        if "context_length" in str(e):
            return "Context limit reached. Please start a new session."

        raise e