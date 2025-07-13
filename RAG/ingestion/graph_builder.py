#
# --- REMPLACEZ TOUT LE FICHIER RAG/ingestion/graph_builder.py PAR CECI ---
#
"""
Knowledge graph builder using a local SQLite database.
This module is responsible for creating and populating the code graph.
"""

import os
import logging
import asyncio
import aiosqlite # La bibliothèque pour l'accès asynchrone à SQLite

logger = logging.getLogger(__name__)

DB_FILE = "code_graph.sqlite"

class SQLiteGraphBuilder:
    """Builds and manages a knowledge graph in a SQLite database."""
    
    def __init__(self):
        """Initialize graph builder."""
        self.db_path = DB_FILE
        self.conn = None
        self._initialized = False

    async def initialize(self):
        """Initialize DB connection and create tables if they don't exist."""
        if self._initialized:
            return
        try:
            self.conn = await aiosqlite.connect(self.db_path)
            await self._create_tables_if_not_exists()
            self._initialized = True
            logger.info(f"SQLite graph builder initialized. Database at: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize SQLiteGraphBuilder: {e}")
            raise

    async def close(self):
        """Close the database connection."""
        if self.conn:
            await self.conn.close()
            self.conn = None
            self._initialized = False
            logger.info("SQLite graph connection closed.")

    async def _create_tables_if_not_exists(self):
        """Creates the necessary tables for the graph."""
        async with self.conn.cursor() as cursor:
            # Table pour les entités (nœuds du graphe)
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS entities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    file_path TEXT,
                    UNIQUE(name, type, file_path)
                )
            """)
            
            # Table pour les relations (arêtes du graphe)
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_id INTEGER NOT NULL,
                    target_id INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    FOREIGN KEY (source_id) REFERENCES entities(id),
                    FOREIGN KEY (target_id) REFERENCES entities(id)
                )
            """)
        await self.conn.commit()

    async def clean_db(self):
        """Deletes the SQLite database file to start fresh."""
        logger.warning(f"Attempting to clean graph database by deleting {self.db_path}")
        if self._initialized:
            await self.close()
        
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            logger.info(f"Deleted existing SQLite database file: {self.db_path}")

    async def add_data_to_graph(self, file_data: dict) -> dict:
        """
        Adds entities and relationships from parsed data to the graph.
        
        Args:
            file_data: A dictionary representing one file from MOCK_DATA.
        
        Returns:
            A dictionary with processing results.
        """
        if not self._initialized:
            await self.initialize()

        entities_added = 0
        relations_added = 0
        
        async with self.conn.cursor() as cursor:
            # 1. Ajouter l'entité du fichier lui-même
            file_path = file_data['file_path']
            await cursor.execute(
                "INSERT OR IGNORE INTO entities (name, type, file_path) VALUES (?, ?, ?)",
                (file_path, 'FILE', file_path)
            )
            
            # 2. Ajouter les entités (fonctions, classes)
            for entity in file_data.get('entities', []):
                await cursor.execute(
                    "INSERT OR IGNORE INTO entities (name, type, file_path) VALUES (?, ?, ?)",
                    (entity['name'], entity['type'], file_path)
                )
            entities_added = self.conn.total_changes
            
            # 3. Ajouter les relations
            for rel in file_data.get('relationships', []):
                # Récupérer les ID de la source et de la cible
                await cursor.execute("SELECT id FROM entities WHERE name = ?", (rel['source'],))
                source_row = await cursor.fetchone()
                
                await cursor.execute("SELECT id FROM entities WHERE name = ?", (rel['target'],))
                target_row = await cursor.fetchone()

                if source_row and target_row:
                    source_id = source_row[0]
                    target_id = target_row[0]
                    await cursor.execute(
                        "INSERT INTO relationships (source_id, target_id, type) VALUES (?, ?, ?)",
                        (source_id, target_id, rel['type'])
                    )
                else:
                    logger.warning(f"Could not find source/target for relationship: {rel}")

        await self.conn.commit()
        relations_added = self.conn.total_changes - entities_added
        
        return {"entities_added": entities_added, "relations_added": relations_added}


# Factory function pour garder la cohérence avec le reste du code
def create_graph_builder() -> SQLiteGraphBuilder:
    """Create graph builder instance."""
    return SQLiteGraphBuilder()