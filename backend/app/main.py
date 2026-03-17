from fastapi import FastAPI
from app.pipelines.rag_pipeline import run_rag
from app.db.mongo_service import get_session, get_sessions
import uvicorn
import os
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Medical RAG Backend")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ask")
async def ask(query: str, session_id: str, use_context: bool = True):

    answer = await run_rag(session_id, query, use_context)

    return {
        "query": query,
        "answer": answer
    }


@app.get("/session/{session_id}")
async def get_session_api(session_id: str):

    return await get_session(session_id)


@app.get("/sessions")
async def get_sessions_api():

    return await get_sessions()


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT")),
        reload=True
    )