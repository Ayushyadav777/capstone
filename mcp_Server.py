"""MCP server for searching and fetching PubMed research papers."""

import requests
import json
from mcp.server.fastmcp import FastMCP
from typing import Optional
import xml.etree.ElementTree as ET

server = FastMCP(
    name="pubmed-research-server",
    instructions="An MCP server that searches PubMed for research papers and fetches their abstracts.",
    host="127.0.0.1",
    port=8020,
)


@server.tool()
def server_health() -> dict:
    """Check the health status of the PubMed MCP server."""
    return {
        "status": "healthy",
        "service": "PubMed Research Server",
        "version": "1.0",
        "available_tools": ["search_papers", "fetch_abstracts", "server_health"]
    }


@server.tool()
def search_papers(
    query: str,
    max_results: int = 10,
    min_year: Optional[int] = None
) -> dict:
    """
    Search PubMed for research papers matching a query.
    
    Args:
        query: Search term (e.g., "pancreatic cancer", "machine learning")
        max_results: Maximum number of results (default: 10)
        min_year: Optional minimum publication year filter
    
    Returns:
        Dictionary with paper IDs and search metadata
    """
    try:
        search_query = query
        if min_year:
            search_query += f" AND {min_year}[PDAT]"
        
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": search_query,
            "retmode": "json",
            "retmax": max_results
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        result_dict = data.get("esearchresult", {})
        paper_ids = result_dict.get("idlist", [])
        total_count = int(result_dict.get("count", 0))
        
        return {
            "status": "success",
            "query": query,
            "total_papers_found": total_count,
            "papers_retrieved": len(paper_ids),
            "paper_ids": paper_ids
        }
    
    except Exception as e:
        return {"status": "error", "message": f"Search failed: {str(e)}"}


@server.tool()
def fetch_abstracts(paper_ids: str) -> dict:
    """
    Fetch abstracts and metadata for specific PubMed papers.
    
    Args:
        paper_ids: Comma-separated PubMed IDs (e.g., "41820251,41831408")
    
    Returns:
        Dictionary with paper details (title, abstract, authors, journal, date)
    """
    try:
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        params = {
            "db": "pubmed",
            "id": paper_ids,
            "rettype": "abstract",
            "retmode": "xml"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        papers = []
        root = ET.fromstring(response.content)
        
        for article in root.findall(".//PubmedArticle"):
            paper_info = {}
            
            pmid_elem = article.find(".//PMID")
            if pmid_elem is not None:
                paper_info["pmid"] = pmid_elem.text
            
            title_elem = article.find(".//ArticleTitle")
            if title_elem is not None:
                paper_info["title"] = title_elem.text
            
            abstract_elem = article.find(".//AbstractText")
            paper_info["abstract"] = abstract_elem.text if abstract_elem is not None else "No abstract"
            
            pub_date = article.find(".//PubDate")
            if pub_date is not None:
                year = pub_date.find("Year")
                if year is not None:
                    paper_info["year"] = year.text
            
            authors = []
            for author in article.findall(".//Author"):
                last_name = author.find("LastName")
                if last_name is not None:
                    author_name = last_name.text
                    first_name = author.find("ForeName")
                    if first_name is not None:
                        author_name += f", {first_name.text}"
                    authors.append(author_name)
            if authors:
                paper_info["authors"] = authors[:5]
            
            journal = article.find(".//Journal/Title")
            if journal is not None:
                paper_info["journal"] = journal.text
            
            papers.append(paper_info)
        
        return {"status": "success", "papers_count": len(papers), "papers": papers}
    
    except Exception as e:
        return {"status": "error", "message": f"Fetch failed: {str(e)}"}


if __name__ == "__main__":
    server.run(transport="sse")