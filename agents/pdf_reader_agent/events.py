from typing import Optional
from llama_index.core.workflow import Event

class InitializeEvent(Event):
    pass

class ConciergeEvent(Event):
    request: Optional[str]
    just_completed: Optional[str]
    need_help: Optional[bool]

class OrchestratorEvent(Event):
    request: Optional[str] = None

class PDFIngestionEvent(Event):
    request: Optional[str]

