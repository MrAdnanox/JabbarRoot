"""
Tools for the Pydantic AI agent.
These functions provide the agent with its core capabilities for search and data retrieval.
"""
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from pydantic import BaseModel, Field

# IMPORTATIONS STRATÉGIQUES : Dépendance aux contrats et injection des implémentations.
from core.contracts.repository_contract import ICodeRepository
from core.contracts.vector_repository_contract import IVectorRepository
from ingestion.storage.repositories.sqlite_graph_repository import SQLiteGraphRepository
from ingestion.storage.repositories.postgres_repository import PostgresRepository
from core.models.db import ChunkResult, GraphSearchResult, DocumentMetadata # <--- CORRIGÉ
from ingestion.embedder import create_embedder


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# INSTANCIATION DES REPOSITORIES : Point unique de vérité pour les implémentations.
code_repository: ICodeRepository = SQLiteGraphRepository()
vector_repository: IVectorRepository = PostgresRepository()
embedder = create_embedder()

class GraphSearchInput(BaseModel):
    query: str = Field(..., description="The exact name of the code entity.")

# --- Tool Input Models ---
class VectorSearchInput(BaseModel):
    query: str = Field(..., description="Search query")
    limit: int = Field(default=10, description="Maximum number of results")

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
    """Perform vector similarity search."""
    try:
        embedding = await embedder.embed_query(input_data.query)
        # APPEL AU CONTRAT
        return await vector_repository.vector_search(embedding=embedding, limit=input_data.limit)
    except Exception as e:
        logger.error(f"Vector search tool failed: {e}", exc_info=True)
        return []

async def graph_search_tool(input_data: GraphSearchInput) -> List[GraphSearchResult]:
    """Search the code knowledge graph for entity relationships."""
    try:
        results = await code_repository.find_entity_relationships(entity_name=input_data.query)
        formatted_results = []
        for res in results:
            fact_string = f"{res['source']} --[{res['relationship']}]--> {res['target']}"
            formatted_results.append(
                GraphSearchResult(
                    fact=fact_string,
                    uuid=str(uuid.uuid4()),
                    source_node_uuid=None
                )
            )
        return formatted_results
    except Exception as e:
        logger.error(f"Graph search tool failed: {e}", exc_info=True)
        return []

async def hybrid_search_tool(input_data: HybridSearchInput) -> List[ChunkResult]:
    """Perform hybrid search (vector + keyword)."""
    try:
        embedding = await embedder.embed_query(input_data.query)
        # APPEL AU CONTRAT
        return await vector_repository.hybrid_search(
            embedding=embedding,
            query_text=input_data.query,
            limit=input_data.limit,
            text_weight=input_data.text_weight
        )
    except Exception as e:
        logger.error(f"Hybrid search tool failed: {e}", exc_info=True)
        return []

async def get_document_tool(input_data: DocumentInput) -> Optional[Dict[str, Any]]:
    """Retrieve a complete document."""
    try:
        # APPEL AU CONTRAT
        document = await vector_repository.get_document(input_data.document_id)
        if document:
            chunks = await vector_repository.get_document_chunks(input_data.document_id)
            document["chunks"] = chunks
        return document
    except Exception as e:
        logger.error(f"Document retrieval tool failed: {e}", exc_info=True)
        return None

async def list_documents_tool(input_data: DocumentListInput) -> List[DocumentMetadata]:
    """List available documents."""
    try:
        # APPEL AU CONTRAT
        return await vector_repository.list_documents(limit=input_data.limit, offset=input_data.offset)
    except Exception as e:
        logger.error(f"Document listing tool failed: {e}", exc_info=True)
        return []