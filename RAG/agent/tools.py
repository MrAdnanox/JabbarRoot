# --- NOUVEAU CONTENU POUR RAG/agent/tools.py ---
"""
Tools for the Pydantic AI agent.
These functions provide the agent with its core capabilities for search and data retrieval.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import uuid

from pydantic import BaseModel, Field
from dotenv import load_dotenv

# --- MODIFICATION : L'import incorrect de ".tools" est remplacé par ".db_utils" ---
from .db_utils import (
    vector_search,
    hybrid_search,
    get_document,
    list_documents,
    get_document_chunks
)
from .graph_utils import (
    search_code_graph
)
from .models import ChunkResult, GraphSearchResult, DocumentMetadata

# Load environment variables
load_dotenv()
logger = logging.getLogger(__name__)

# --- MODIFICATION : Correction du chemin d'import pour la cohérence ---
try:
    # Ce chemin est pour l'exécution normale de l'application
    from ingestion.embedder import create_embedder
except ImportError:
    # Ce chemin est pour les cas où le module est exécuté différemment (ex: tests)
    # Ajout d'une gestion de chemin plus robuste
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from ingestion.embedder import create_embedder


embedder = create_embedder()


async def generate_embedding(text: str) -> List[float]:
    """
    Generate an embedding for a single query text using the configured provider.
    """
    try:
        # La méthode correcte dans notre embedder est `embed_query`
        return await embedder.embed_query(text)
    except Exception as e:
        logger.error(f"Failed to generate query embedding: {e}")
        return [0.0] * embedder.get_embedding_dimension()


# --- Tool Input Models ---

class VectorSearchInput(BaseModel):
    query: str = Field(..., description="Search query")
    limit: int = Field(default=10, description="Maximum number of results")

class GraphSearchInput(BaseModel):
    query: str = Field(..., description="Search query for a code entity (function, class, etc.)")

class HybridSearchInput(BaseModel):
    query: str = Field(..., description="Search query")
    limit: int = Field(default=10, description="Maximum number of results")
    text_weight: float = Field(default=0.3, description="Weight for text similarity (0-1)")

class DocumentInput(BaseModel):
    document_id: str = Field(..., description="Document ID to retrieve")

class DocumentListInput(BaseModel):
    limit: int = Field(default=20, description="Maximum number of documents")
    offset: int = Field(default=0, description="Number of documents to skip")


# --- Tool Implementation Functions ---

async def vector_search_tool(input_data: VectorSearchInput) -> List[ChunkResult]:
    """
    Perform vector similarity search.
    """
    try:
        embedding = await generate_embedding(input_data.query)
        results = await vector_search(embedding=embedding, limit=input_data.limit)
        return [
            ChunkResult(
                chunk_id=str(r["chunk_id"]),
                document_id=str(r["document_id"]),
                content=r["content"],
                score=r["similarity"],
                metadata=r["metadata"],
                document_title=r["document_title"],
                document_source=r["document_source"]
            ) for r in results
        ]
    except Exception as e:
        logger.error(f"Vector search tool failed: {e}")
        return []

async def graph_search_tool(input_data: GraphSearchInput) -> List[GraphSearchResult]:
    """
    Search the code knowledge graph for entity relationships.
    """
    try:
        results = await search_code_graph(query=input_data.query)
        
        formatted_results = []
        for res in results:
            fact_string = f"{res['source']} --[{res['relationship']}]--> {res['target']}"
            
            formatted_results.append(
                GraphSearchResult(
                    fact=fact_string,
                    uuid=str(uuid.uuid4()),
                    source_node_uuid=None # Ce champ n'est plus pertinent avec SQLite
                )
            )
        return formatted_results
    except Exception as e:
        logger.error(f"Graph search tool failed: {e}")
        return []

async def hybrid_search_tool(input_data: HybridSearchInput) -> List[ChunkResult]:
    """
    Perform hybrid search (vector + keyword).
    """
    try:
        embedding = await generate_embedding(input_data.query)
        results = await hybrid_search(
            embedding=embedding,
            query_text=input_data.query,
            limit=input_data.limit,
            text_weight=input_data.text_weight
        )
        return [
            ChunkResult(
                chunk_id=str(r["chunk_id"]),
                document_id=str(r["document_id"]),
                content=r["content"],
                score=r["combined_score"],
                metadata=r["metadata"],
                document_title=r["document_title"],
                document_source=r["document_source"]
            ) for r in results
        ]
    except Exception as e:
        logger.error(f"Hybrid search tool failed: {e}")
        return []

async def get_document_tool(input_data: DocumentInput) -> Optional[Dict[str, Any]]:
    """
    Retrieve a complete document.
    """
    try:
        document = await get_document(input_data.document_id)
        if document:
            chunks = await get_document_chunks(input_data.document_id)
            document["chunks"] = chunks
        return document
    except Exception as e:
        logger.error(f"Document retrieval tool failed: {e}")
        return None

async def list_documents_tool(input_data: DocumentListInput) -> List[DocumentMetadata]:
    """
    List available documents.
    """
    try:
        documents = await list_documents(limit=input_data.limit, offset=input_data.offset)
        return [
            DocumentMetadata(
                id=d["id"],
                title=d["title"],
                source=d["source"],
                metadata=d["metadata"],
                created_at=datetime.fromisoformat(d["created_at"]),
                updated_at=datetime.fromisoformat(d["updated_at"]),
                chunk_count=d.get("chunk_count")
            ) for d in documents
        ]
    except Exception as e:
        logger.error(f"Document listing tool failed: {e}")
        return []