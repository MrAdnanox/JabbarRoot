from abc import ABC, abstractmethod
from typing import List, Any
from ..models.graph import CodeGraph

class ICodeRepository(ABC):
    """Contrat pour la persistance et la récupération de la connaissance du code."""

    @abstractmethod
    async def save_graph(self, graph: CodeGraph) -> None:
        """Persiste le graphe de connaissance du code."""
        pass

    @abstractmethod
    async def get_function_calls(self, function_name: str) -> List[str]:
        """Récupère les fonctions appelées par une fonction donnée."""
        pass