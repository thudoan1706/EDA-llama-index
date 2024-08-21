# events.py

from llama_index.core.workflow import Event
from typing import List, Dict

class ReasoningEvent(Event):
    input_data: List[str]