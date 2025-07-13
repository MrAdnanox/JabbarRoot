# analyzer-engine/ingestion/parsing/parser_registry.py
from typing import List, Type
from ...core.contracts.parser import IParser

class ParserRegistry:
    """Registre pour trouver le parseur adéquat."""
    def __init__(self):
        self._parsers: List[IParser] = []

    def register(self, parser: IParser):
        self._parsers.append(parser)

    def get_parser(self, language: str) -> IParser:
        for parser in self._parsers:
            if parser.supports_language(language):
                return parser
        raise ValueError(f"No parser found for language: {language}")


# Exemple de registre "singleton"
parser_registry = ParserRegistry()
# Dans le futur, on y enregistrera les parseurs au démarrage de l'app.
# from .parsers.python_parser import PythonParser
# parser_registry.register(PythonParser())
