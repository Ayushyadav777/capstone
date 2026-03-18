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

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


async def run_rag(session_id, query, use_context):
    history = await get_chat_history(session_id)

    if use_context:
        logger.info("Getting previous papers (if any)")
        stored_docs = await get_session_papers(session_id)

        logger.info("Creating embeddings")
        query_embedding, token_count = create_embedding(query)
        logger.info(f"Token Usage: {token_count}")

        logger.info("Retrieving chunks")
        docs = await retrieve_similar(query_embedding, stored_docs)

        logger.info("Reranking")
        ranked = await rerank(query, docs)

        logger.info("Generating final answer")
        answer, token_count, eval = await generate_answer(query, ranked, history, use_context)
        logger.info(f"DeepEval: {eval}")


        await store_chat(session_id, query, answer, query)

        logger.info(f"Token Usage: {token_count}")
    else:
        logger.info("Query analyzing")
        phrase, token_count = await extract_search_phrase(query)
        logger.info(f"Token Usage: {token_count}")

        logger.info("Searching for papers")
        pmids = await search_pubmed(phrase)

        logger.info("Storing papers")
        papers, token_count = await ingest_and_store_papers(session_id, pmids)
        logger.info(f"Token Usage: {token_count}")

        logger.info("Getting previous papers (if any)")
        stored_docs = await get_session_papers(session_id)

        logger.info("Creating embeddings")
        query_embedding, token_count = create_embedding(query)
        logger.info(f"Token Usage: {token_count}")

        logger.info("Retrieving chunks")
        docs = await retrieve_similar(query_embedding, stored_docs)

        logger.info("Reranking")
        ranked = await rerank(query, docs)

        logger.info("Generating final answer")
        answer, token_count, eval = await generate_answer(query, ranked, history, use_context)
        logger.info(f"DeepEval: {eval}")

        await store_chat(session_id, query, answer, phrase)

        logger.info(f"Token Usage: {token_count}")
    return answer