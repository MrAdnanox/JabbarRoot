# analyzer-engine/ingestion/orchestration/execution_context.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from core.models.ast_models import NormalizedAST

class ExecutionContext(BaseModel):
    """L'objet qui circule entre les étapes du pipeline, transportant l'état."""
    # Données initiales
    file_path: str
    source_code: str
    language: str
    
    # Données enrichies par les étapes successives
    normalized_ast: Optional[NormalizedAST] = None # <-- AJOUT
    entities: List[Dict[str, Any]] = []
    relationships: List[Dict[str, Any]] = []
    chunks: List[Dict[str, Any]] = []
    
    class Config:
        arbitrary_types_allowed = True