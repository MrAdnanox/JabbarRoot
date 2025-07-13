
# analyzer-engine/ingestion/orchestration/execution_context.py
from pydantic import BaseModel
from typing import Optional
from ...core.models.ast import NormalizedAST
from ...core.models.graph import CodeGraph

class ExecutionContext(BaseModel):
    """L'objet qui circule entre les étapes du pipeline, transportant l'état."""
    source_code: str
    language: str
    
    # Enrichi par les étapes successives
    normalized_ast: Optional[NormalizedAST] = None
    code_graph: Optional[CodeGraph] = None
    
    class Config:
        arbitrary_types_allowed = True # Permet d'avoir des objets complexes