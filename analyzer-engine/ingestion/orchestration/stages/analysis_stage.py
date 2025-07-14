# Fichier : analyzer-engine/ingestion/orchestration/stages/analysis_stage.py
import logging
import os  # <=============================== AJOUTER CET IMPORT
from .base_stage import IPipelineStage
from ..execution_context import ExecutionContext
from core.models.ast_models import ASTNode

logger = logging.getLogger(__name__)

class AnalysisStage(IPipelineStage):
    """
    Étape responsable de l'analyse de l'AST pour extraire entités et relations.
    """

    async def execute(self, context: ExecutionContext) -> ExecutionContext:
        logger.info(f"AnalysisStage: Analyzing AST for {context.file_path}")
        
        if not context.normalized_ast:
            logger.warning(f"No AST found for {context.file_path}, skipping analysis.")
            return context

        entities = []
        relationships = []
        
        # ======================= MODIFICATION CI-DESSOUS =======================
        
        # 1. Créer une entité pour le fichier lui-même.
        #    On utilise le chemin relatif comme nom pour l'unicité.
        file_entity_name = context.file_path
        entities.append({
            "type": "FILE",
            "name": file_entity_name,
            "source_code": context.source_code # Le code source complet du fichier
        })
        
        # 2. Parcourir l'AST pour trouver les autres entités et les lier à l'entité fichier.
        self._traverse_ast(
            node=context.normalized_ast.root, 
            entities=entities, 
            relationships=relationships,
            file_entity_name=file_entity_name # Passer le nom du fichier comme parent
        )
        
        # ======================= FIN DE LA MODIFICATION ======================
        
        context.entities = entities
        context.relationships = relationships
        
        logger.info(f"Extracted {len(context.entities)} entities and {len(context.relationships)} relationships from AST.")
        return context

    def _traverse_ast(self, node: ASTNode, entities: list, relationships: list, file_entity_name: str):
        """Parcourt l'AST pour trouver des entités et des relations simples."""
        
        if node.node_type in ("FunctionDef", "AsyncFunctionDef", "ClassDef"):
            entity_type_map = {
                "FunctionDef": "FUNCTION",
                "AsyncFunctionDef": "FUNCTION",
                "ClassDef": "CLASS",
            }
            entity_name = node.name
            entities.append({
                "type": entity_type_map[node.node_type],
                "name": entity_name,
                "source_code": f"# Source code for {entity_name} would be extracted here"
            })
            
            # ======================= MODIFICATION CI-DESSOUS =======================
            # La relation est maintenant entre l'entité (fonction/classe) et le nom du fichier.
            relationships.append({
                "source": entity_name, 
                "target": file_entity_name, # <-- Utilise le nom du fichier passé en paramètre
                "type": "DEFINES_IN_FILE"
            })
            # ======================= FIN DE LA MODIFICATION ======================

        for child in node.children:
            self._traverse_ast(child, entities, relationships, file_entity_name)