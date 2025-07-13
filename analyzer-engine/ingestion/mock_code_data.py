# DANS LE NOUVEAU FICHIER : ingestion/mock_code_data.py

MOCK_DATA = {
  "files": [
    {
      "file_path": "agent/api.py",
      "entities": [
        {"type": "FUNCTION", "name": "execute_agent", "source_code": "def execute_agent(...): ..."},
        {"type": "FUNCTION", "name": "get_or_create_session", "source_code": "def get_or_create_session(...): ..."}
      ],
      "relationships": [
        {"source": "execute_agent", "target": "get_or_create_session", "type": "CALLS"}
      ]
    },
    {
      "file_path": "agent/models.py",
      "entities": [
        {"type": "CLASS", "name": "ChatRequest", "source_code": "class ChatRequest(BaseModel): ..."}
      ],
      "relationships": [
        {"source": "execute_agent", "target": "ChatRequest", "type": "USES_TYPE"}
      ]
    }
  ]
}