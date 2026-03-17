# Medical Literature RAG System

## System Overview
**Medical Literature RAG (Retrieval-Augmented Generation) System** that enables researchers and healthcare professionals to search, retrieve, and analyze scientific publications from PubMed with AI-powered responses.

## Project Structure
```
backend/
├── app/
│   ├── db/mongo_service.py          # MongoDB document storage
│   ├── ingestion/pubmed_service.py  # PubMed API ingestion
│   ├── main.py                       # API entry point
│   ├── pipelines/rag_pipeline.py    # RAG orchestration
│   └── services/
│       ├── embedding_service.py     # Text embedding generation
│       ├── llm_service.py           # LLM integration
│       ├── query_norm.py            # Query normalization
│       ├── reranker.py              # Results reranking
│       ├── similarity_search.py     # Vector similarity search
│       └── vector_store.py          # Vector database operations
├── requirements.txt
frontend/
├── index.html
├── script.js
└── style.css
```

## Required Diagram Sections

### 1. System Architecture Overview
- **Frontend Layer**: Web interface (HTML/CSS/JS)
- **API Layer**: REST API (Python/FastAPI assumed)
- **Service Layer**: Core business logic services
- **Data Layer**: Storage systems (MongoDB, Vector Store)
- **External Services**: PubMed API, LLM Provider

### 2. Component Diagram

- **PubMed Ingestion Service**: Fetches publications via PubMed API
- **Embedding Service**: Generates vector embeddings for documents
- **Vector Store**: Stores and indexes document embeddings
- **MongoDB Service**: Stores raw documents and metadata
- **Similarity Search Service**: Performs vector similarity queries
- **Reranker Service**: Reorders search results by relevance
- **LLM Service**: Generates AI responses using retrieved context
- **Query Normalizer**: Preprocesses user queries
- **RAG Pipeline**: Orchestrates the entire retrieval-generation flow

### 3. Data Flow Diagram
Illustrate the flow for:
- **Document Ingestion Flow**:
  1. PubMed API → PubMed Service → Embedding Service → Vector Store
  2. Raw documents → MongoDB Service → Document Storage
  
- **Query Flow**:
  1. User Query → Query Normalizer → Similarity Search → Reranker
  2. Retrieved Context + Query → LLM Service → AI Response
  3. Response → Frontend → User

### 4. Technology Stack
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Backend**: Python
- **Database**: MongoDB (document storage)
- **Vector Database**: [Specify based on implementation]
- **LLM**: [Specify provider - OpenAI, Anthropic, local, etc.]
- **External APIs**: PubMed E-utilities API

### 5. API Endpoints
Document key REST endpoints (infer from structure):
- `POST /api/ingest` - Trigger document ingestion
- `GET /api/search` - Search publications
- `POST /api/query` - RAG query with AI response
- `GET /api/documents/{id}` - Get document by ID

