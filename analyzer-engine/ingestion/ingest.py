#
# --- REMPLACEZ LE CONTENU DE RAG/ingestion/ingest.py PAR CECI ---
#
"""
Main ingestion script for processing mock code data into vector DB and a local graph DB.
"""

import os
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import argparse
import json # <-- Ajout de l'import json

from dotenv import load_dotenv

from .chunker import create_chunker, DocumentChunk
from .embedder import create_embedder
from .graph_builder import create_graph_builder

# Import agent utilities and our new mock data source
try:
    from ..agent.db_utils import initialize_database, close_database, db_pool
    from ..agent.models import IngestionConfig, IngestionResult
    from .mock_code_data import MOCK_DATA
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from agent.db_utils import initialize_database, close_database, db_pool
    from agent.models import IngestionConfig, IngestionResult
    from ingestion.mock_code_data import MOCK_DATA


# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class CodeIngestionPipeline:
    """Pipeline for ingesting mock code data."""
    
    def __init__(
        self,
        config: IngestionConfig,
        clean_before_ingest: bool = False
    ):
        """Initialize ingestion pipeline."""
        self.config = config
        self.clean_before_ingest = clean_before_ingest
        
        self.chunker = create_chunker(self.config) 
        self.embedder = create_embedder()
        self.graph_builder = create_graph_builder()
        
        self._initialized = False
    
    async def initialize(self):
        """Initialize database connections."""
        if self._initialized:
            return
        
        logger.info("Initializing ingestion pipeline...")
        await initialize_database()
        await self.graph_builder.initialize()
        self._initialized = True
        logger.info("Ingestion pipeline initialized")
    
    async def close(self):
        """Close database connections."""
        if self._initialized:
            await self.graph_builder.close()
            await close_database()
            self._initialized = False
    
    async def _save_to_postgres(self, file_path: str, chunks: List[DocumentChunk]):
        """
        Saves a document and its chunks to PostgreSQL.
        
        Args:
            file_path: The path of the source file, used as the document identifier.
            chunks: A list of DocumentChunk objects with embeddings.
        """
        if not chunks:
            logger.warning(f"No chunks to save for {file_path}")
            return 0

        async with db_pool.acquire() as conn:
            # 1. Créer le document parent
            # On utilise le chemin du fichier comme titre et source pour la simplicité
            # Le contenu est une note indiquant qu'il s'agit d'un conteneur pour les chunks de code
            document_content = f"This is a container document for code chunks from the file: {file_path}."
            
            try:
                document_id = await conn.fetchval(
                    """
                    INSERT INTO documents (title, source, content, metadata)
                    VALUES ($1, $2, $3, $4)
                    RETURNING id
                    """,
                    file_path,
                    file_path,
                    document_content,
                    json.dumps({"file_path": file_path, "ingested_at": datetime.now().isoformat()})
                )
                
                # 2. Préparer et insérer les chunks en batch
                chunks_to_insert = []
                for chunk in chunks:
                    if chunk.embedding is None:
                        logger.warning(f"Skipping chunk {chunk.index} for {file_path} due to missing embedding.")
                        continue
                    
                    # pgvector attend une chaîne de caractères, pas une liste
                    embedding_str = str(chunk.embedding)
                    
                    chunks_to_insert.append((
                        document_id,
                        chunk.content,
                        embedding_str,
                        chunk.index,
                        json.dumps(chunk.metadata),
                        chunk.token_count
                    ))
                
                if not chunks_to_insert:
                    logger.warning(f"No valid chunks with embeddings to insert for document {file_path}")
                    return 0

                await conn.executemany(
                    """
                    INSERT INTO chunks (document_id, content, embedding, chunk_index, metadata, token_count)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    """,
                    chunks_to_insert
                )
                
                logger.info(f"Successfully saved {len(chunks_to_insert)} chunks for document {file_path} (ID: {document_id})")
                return len(chunks_to_insert)

            except Exception as e:
                logger.error(f"Failed to save document/chunks for {file_path} to PostgreSQL: {e}", exc_info=True)
                # Dans une vraie application, on pourrait vouloir une transaction et un rollback ici
                return 0

    async def ingest_mock_data(
        self,
        progress_callback: Optional[callable] = None
    ) -> List[IngestionResult]:
        """
        Ingest all data from the mock data source.
        """
        if not self._initialized:
            await self.initialize()
        
        if self.clean_before_ingest:
            await self._clean_databases()
        
        mock_files_to_process = MOCK_DATA['files']
        total_files = len(mock_files_to_process)
        logger.info(f"Found {total_files} mock files to process from MOCK_DATA.")
        
        results = []
        
        for i, file_data in enumerate(mock_files_to_process):
            file_path = file_data['file_path']
            start_time = datetime.now()
            errors = []
            
            try:
                logger.info(f"--- Processing mock file {i+1}/{total_files}: {file_path} ---")
                
                # 1. Graphe : Envoyer les données au constructeur de graphe
                graph_result = await self.graph_builder.add_data_to_graph(file_data)
                logger.info(f"Graph Builder Result: {graph_result}")
                
                # 2. Chunks : Créer les chunks à partir des entités (fonctions/classes)
                logger.info(f"Creating chunks for {len(file_data['entities'])} entities in {file_path}...")
                chunks = self.chunker.chunk_from_entities(
                    entities=file_data['entities'],
                    file_path=file_path,
                    base_metadata={'source': file_path}
                )
                logger.info(f"Created {len(chunks)} chunks from entities.")

                # 3. Embeddings : Créer les embeddings pour chaque chunk
                logger.info(f"Generating embeddings for {len(chunks)} chunks...")
                embedded_chunks = await self.embedder.embed_chunks(chunks)
                logger.info(f"Generated embeddings for {len(embedded_chunks)} chunks.")

                # 4. Sauvegarde : Sauvegarder dans PostgreSQL
                chunks_saved = await self._save_to_postgres(file_path, embedded_chunks)
                
                processing_time = (datetime.now() - start_time).total_seconds() * 1000
                
                ingestion_result = IngestionResult(
                    document_id=file_path, # Using file_path as a unique ID for this mock run
                    title=file_path,
                    chunks_created=chunks_saved,
                    entities_extracted=graph_result.get('entities_added', 0),
                    relationships_created=graph_result.get('relations_added', 0),
                    processing_time_ms=processing_time,
                    errors=errors
                )
                results.append(ingestion_result)
                
                logger.info(f"SUCCESS for {file_path}. Result: {ingestion_result.model_dump_json(indent=2)}")
                
                if progress_callback:
                    progress_callback(i + 1, total_files)
                
            except Exception as e:
                logger.error(f"Failed to process mock data for {file_path}: {e}", exc_info=True)
                errors.append(str(e))
        
        logger.info("Ingestion of mock data complete.")
        return results
    
    async def _clean_databases(self):
        """Clean existing data from databases."""
        logger.warning("Cleaning existing data from databases...")
        
        async with db_pool.acquire() as conn:
            await conn.execute("TRUNCATE TABLE messages, sessions, chunks, documents RESTART IDENTITY CASCADE")
        logger.info("Cleaned PostgreSQL database")
        
        await self.graph_builder.clean_db()
        logger.info("Cleaned Graph (SQLite) database")


async def main():
    """Main function for running ingestion."""
    parser = argparse.ArgumentParser(description="Ingest mock code data.")
    parser.add_argument("--clean", "-c", action="store_true", help="Clean existing data before ingestion")
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    
    config = IngestionConfig()
    
    pipeline = CodeIngestionPipeline(config=config, clean_before_ingest=args.clean)
    
    try:
        await pipeline.initialize()
        await pipeline.ingest_mock_data()
    except Exception as e:
        logger.error(f"Ingestion pipeline failed: {e}", exc_info=True)
    finally:
        await pipeline.close()


if __name__ == "__main__":
    asyncio.run(main())