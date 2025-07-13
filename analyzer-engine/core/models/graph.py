from pydantic import BaseModel
from typing import List, Dict, Any

class GraphNode(BaseModel):
    id: str
    type: str # 'FUNCTION', 'CLASS', 'FILE'
    properties: Dict[str, Any]

class Relationship(BaseModel):
    source_id: str
    target_id: str
    type: str # 'CALLS', 'IMPORTS', 'DEFINES'

class CodeGraph(BaseModel):
    nodes: List[GraphNode]
    relationships: List[Relationship]