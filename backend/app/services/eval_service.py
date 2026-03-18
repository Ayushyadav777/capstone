import asyncio
from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

def evaluate_response_sync(query: str, answer: str, papers: list):

    try:
        retrieval_context = [
            f"{p['title']} {p['abstract']}"[:1000]
            for p in papers
        ]

        test_case = LLMTestCase(
            input=query,
            actual_output=answer,
            retrieval_context=retrieval_context
        )

        # ✅ IMPORTANT: disable async mode
        faithfulness = FaithfulnessMetric(async_mode=False)
        relevancy = AnswerRelevancyMetric(async_mode=False)

        faithfulness_score = faithfulness.measure(test_case)
        relevancy_score = relevancy.measure(test_case)

        return {
            "faithfulness": faithfulness_score,
            "relevancy": relevancy_score
        }

    except Exception as e:
        logger.info(f"DeepEval: {eval}")
        return {
            "faithfulness": None,
            "relevancy": None
        }


# ✅ Wrapper for FastAPI (async safe)
async def evaluate_response_safe(query, answer, papers):
    return await asyncio.to_thread(
        evaluate_response_sync,
        query,
        answer,
        papers
    )