from typing import Any, List, Tuple
from llama_index.core.tools.types import AsyncBaseTool
from llama_index.core.workflow import Workflow, Context, Event, StartEvent, StopEvent, step
import os
from llama_index.core.tools import FunctionTool


class FunctionCallEvent(Event):
    func_call: Tuple[str, str, str]  # Function name, raw inputs, output placeholder

class ValidateFunctionCallEvent(Event):
    input_data: List[Any]
    output_placeholder: str
    tool_output: Any

class InitializeEvent(Event):
    """Event for initializing the workflow context."""
    pass