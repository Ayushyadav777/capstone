import os
import httpx
import asyncio
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("PUBMED_BASE")
RETMAX = int(os.getenv("RETMAX", 10))


import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# ✅ GLOBAL PERSISTENT CLIENT (KEEP-ALIVE)
client = httpx.AsyncClient(
    timeout=httpx.Timeout(None), 
    limits=httpx.Limits(
        max_connections=100,
        max_keepalive_connections=20
    ),
    verify=False
)

# -------------------------------
# SEARCH PUBMED
# -------------------------------
async def search_pubmed(term: str):

    url = f"{BASE_URL}/esearch.fcgi"

    params = {
        "db": "pubmed",
        "term": term,
        "retmode": "json",
        "retmax": RETMAX
    }

    # retry logic
    for attempt in range(3):
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            return data["esearchresult"]["idlist"]

        except httpx.ConnectTimeout:
            logger.info(f"[search_pubmed] Timeout... retry {attempt+1}")
            await asyncio.sleep(2)

        except Exception as e:
            logger.error(f"[search_pubmed] Error: {str(e)}")
            break

    return []


# -------------------------------
# FETCH PAPERS
# -------------------------------
async def fetch_papers(pmids: list[str]):

    if not pmids:
        return []

    url = f"{BASE_URL}/efetch.fcgi"

    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "rettype": "abstract",
        "retmode": "xml"
    }

    # retry logic
    for attempt in range(3):
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            break

        except httpx.ConnectTimeout:
            logger.info(f"[fetch_papers] Timeout... retry {attempt+1}")
            await asyncio.sleep(2)

        except Exception as e:
            logger.error(f"[fetch_papers] Error: {str(e)}")
            return []

    root = ET.fromstring(response.text)

    papers = []

    for article in root.findall(".//PubmedArticle"):

        pmid = article.findtext(".//PMID")
        title = article.findtext(".//ArticleTitle")

        # abstract handling
        abstract = ""
        node = article.find(".//AbstractText")
        if node is not None and node.text:
            abstract = node.text

        journal = article.findtext(".//Journal/Title")

        authors = []
        for author in article.findall(".//Author"):
            last = author.findtext("LastName")
            first = author.findtext("ForeName")

            if last and first:
                authors.append(f"{first} {last}")

        papers.append({
            "pmid": pmid,
            "title": title,
            "abstract": abstract,
            "journal": journal,
            "authors": authors
        })

    return papers


# -------------------------------
# OPTIONAL: CLOSE CLIENT
# -------------------------------
async def close_client():
    await client.aclose()