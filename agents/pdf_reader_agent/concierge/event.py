from typing import Optional
from llama_index.core.workflow import (
    Event
)

class InitializeEvent(Event):
    pass

class ConciergeEvent(Event):
    request: Optional[str]
    just_completed: Optional[str]
    need_help: Optional[bool]

class PDFIngestionEvent(Event):
    dirname: str
