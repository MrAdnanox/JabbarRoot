# analyzer-engine/ingestion/orchestration/pipeline_director.py
from typing import List
from .stages.base_stage import IPipelineStage
from .execution_context import ExecutionContext
from .stages.parsing_stage import ParsingStage
from .stages.analysis_stage import AnalysisStage
from .stages.storage_stage import StorageStage


class PipelineDirector:
    """Le chef d'orchestre : ne connaît que les étapes, pas leur contenu."""

    def __init__(self):
        # Le pipeline est fixe pour cet exemple, mais pourrait être construit par une Factory
        self.pipeline: List[IPipelineStage] = [
            ParsingStage(),
            AnalysisStage(),
            StorageStage(),
        ]

    async def process(self, code: str, language: str):
        context = ExecutionContext(source_code=code, language=language)
        
        print(f"PipelineDirector: Début du traitement pour {language}...")
        for stage in self.pipeline:
            context = await stage.execute(context)
        
        print("PipelineDirector: Traitement terminé.")
        return context.code_graph