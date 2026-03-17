from app.services.query_norm import extract_search_phrase
from app.services.embedding_service import create_embedding
from app.services.similarity_search import retrieve_similar
from app.services.reranker import rerank
from app.services.llm_service import generate_answer
from app.ingestion.pubmed_service import search_pubmed
from app.db.mongo_service import (
    ingest_and_store_papers,
    get_session_papers,
    store_chat,
    get_chat_history
)


async def run_rag(session_id, query, use_context):
    history = await get_chat_history(session_id)

    if use_context:
        print("Getting previous papers(if any)!!")
        stored_docs = await get_session_papers(session_id)
        print("Creating embeddings!!")
        query_embedding = create_embedding(query)
        print("Retrieving chunks!!")
        docs = await retrieve_similar(query_embedding, stored_docs)
        print("Reranking!!")
        ranked = await rerank(query, docs)

        print("Generating final answer!!")
        answer = await generate_answer(query, ranked, history, use_context)
        await store_chat(session_id, query, answer, query)
    else:
        # Fetch new papers and perform RAG
        print("Query analyzing!!")
        phrase = await extract_search_phrase(query)
        print("Searching for papers!!")
        pmids = await search_pubmed(phrase)
        print("Storing papers!!")
        await ingest_and_store_papers(session_id, pmids)

        print("Getting previous papers(if any)!!")
        stored_docs = await get_session_papers(session_id)
        print("Creating embeddings!!")
        query_embedding = create_embedding(query)
        print("Retrieving chunks!!")
        docs = await retrieve_similar(query_embedding, stored_docs)
        print("Reranking!!")
        ranked = await rerank(query, docs)

        print("Generating final answer!!")
        answer = await generate_answer(query, ranked, history, use_context)

        await store_chat(session_id, query, answer, phrase)
    return answer