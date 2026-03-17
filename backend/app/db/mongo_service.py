import os
from motor.motor_asyncio import AsyncIOMotorClient
from app.ingestion.pubmed_service import fetch_papers
from app.services.embedding_service import create_embedding
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB")


client = AsyncIOMotorClient(MONGO_URI)

db = client[DB_NAME]

sessions_collection = db["sessions"]


# -----------------------------
# Get papers for session
# -----------------------------
async def get_session_papers(session_id):

    session = await sessions_collection.find_one(
        {"session_id": session_id},
        {"_id": 0}
    )

    if not session:
        return []

    return session.get("papers", [])


# -----------------------------
# Ingest and store papers
# -----------------------------
async def ingest_and_store_papers(session_id, pmids):

    print("Fetching papers from PubMed...")

    papers_data = await fetch_papers(pmids)

    papers = []

    for paper in papers_data:

        text = f"{paper['title']} {paper['abstract']}"

        embedding = create_embedding(text)

        paper_doc = {
            "pmid": paper["pmid"],
            "title": paper["title"],
            "abstract": paper["abstract"],
            "journal": paper["journal"],
            "authors": paper["authors"],
            "embedding": embedding
        }

        papers.append(paper_doc)

    document = {
        "session_id": session_id,
        "papers": papers,
        "queries": []
    }

    await sessions_collection.update_one(
        {"session_id": session_id},
        {"$set": document},
        upsert=True
    )

    return papers


# -----------------------------
# Store chat
# -----------------------------
async def store_chat(session_id, query, answer, search_term):

    await sessions_collection.update_one(
        {"session_id": session_id},
        {
            "$push": {
                "queries": {
                    "query": query,
                    "answer": answer,
                    "search_term": search_term
                }
            }
        }
    )


# -----------------------------
# Get chat history
# -----------------------------
async def get_chat_history(session_id):

    session = await sessions_collection.find_one({"session_id": session_id})

    if not session:
        return []

    return session.get("queries", [])



# -----------------------------
# Session queries
# -----------------------------
async def get_session(session_id: str):

    doc = await sessions_collection.find_one(
        {"session_id": session_id},
        {"queries": 1, "_id": 0}
    )

    if not doc:
        return {"messages": []}

    messages = []

    for q in doc["queries"]:
        messages.append({
            "role": "user",
            "content": q["query"]
        })

        messages.append({
            "role": "assistant",
            "content": q["answer"]
        })

    return {"messages": messages}



# -----------------------------
# All sessions
# -----------------------------
async def get_sessions():

    docs = sessions_collection.find(
        {},
        {"session_id": 1, "queries": 1, "_id": 0}
    )

    sessions = []

    async for d in docs:

        title = "New Chat"

        if d.get("queries"):
            title = d["queries"][0].get("query", "New Chat")

        sessions.append({
            "session_id": d["session_id"],
            "title": title
        })

    return {"sessions": sessions}