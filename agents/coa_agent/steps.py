from llama_index.core.workflow import (
    Context,
    Workflow,
    StartEvent,
    StopEvent,
    Event,
    step,
)

from events import ReasoningEvent
from llama_index.core.workflow import Context, StartEvent, StopEvent
import time
from llama_index.core import get_response_synthesizer
import os


os.environ["OPENAI_API_KEY"] = ""


class WorkflowSteps:
    
    @step(pass_context=True)
    async def concierge(self, ctx: Context, ev: StartEvent) -> ReasoningEvent | None:
        if isinstance(ev, StartEvent):
            return ReasoningEvent()