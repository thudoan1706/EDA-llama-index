
# workflow.py
from llama_index.core.workflow import Context, StartEvent, Workflow
from .steps import WorkflowSteps
from .events import ReasoningEvent


class ConciergeWorkflow(Workflow):
    
    steps = WorkflowSteps()

    @step(pass_context=True)
    async def concierge(self, ctx: Context, ev: StartEvent) -> ReasoningEvent | None: