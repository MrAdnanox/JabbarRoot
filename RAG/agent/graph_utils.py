#
# --- REMPLACEZ LE CONTENU DE RAG/agent/graph_utils.py PAR CECI ---
#
"""
Graph utilities for querying the local SQLite code graph.
"""

import os
import logging
import aiosqlite
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Le chemin vers la base de données est fixe, car il est créé par le pipeline d'ingestion
DB_FILE = "code_graph.sqlite"

async def search_code_graph(query: str) -> List[Dict[str, Any]]:
    """
    Searches the SQLite code graph for an entity and its direct relationships.

    Args:
        query: The name of the entity (function, class, file) to search for.

    Returns:
        A list of dictionaries, each representing a relationship fact.
    """
    if not os.path.exists(DB_FILE):
        logger.warning(f"Graph database file not found at {DB_FILE}. Ingestion may not have run.")
        return []

    results = []
    try:
        async with aiosqlite.connect(DB_FILE) as db:
            # Utiliser une requête LIKE pour être plus flexible
            search_term = f"%{query}%"
            
            # 1. Trouver les entités correspondantes
            cursor = await db.execute("SELECT id, name, type FROM entities WHERE name LIKE ?", (search_term,))
            entities_found = await cursor.fetchall()
            
            if not entities_found:
                logger.info(f"No entities found matching '{query}' in the graph.")
                return []

            # 2. Pour chaque entité, trouver ses relations
            for entity_id, entity_name, entity_type in entities_found:
                # Requête pour trouver les relations où l'entité est la source OU la cible
                rel_cursor = await db.execute("""
                    SELECT
                        s.name as source_name,
                        s.type as source_type,
                        r.type as rel_type,
                        t.name as target_name,
                        t.type as target_type
                    FROM relationships r
                    JOIN entities s ON r.source_id = s.id
                    JOIN entities t ON r.target_id = t.id
                    WHERE r.source_id = ? OR r.target_id = ?
                """, (entity_id, entity_id))
                
                relationships = await rel_cursor.fetchall()
                
                for rel in relationships:
                    # Formatter le résultat pour être facilement compréhensible par le LLM
                    fact = {
                        "source": f"{rel[0]} ({rel[1]})",
                        "relationship": rel[2],
                        "target": f"{rel[3]} ({rel[4]})"
                    }
                    if fact not in results:
                        results.append(fact)

    except Exception as e:
        logger.error(f"Error querying code graph: {e}", exc_info=True)

    return results