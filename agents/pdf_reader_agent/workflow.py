from .orchestrator.ingestion.vector_store.pinecone.client import PineconeClient
from llama_index.core.workflow import (
    Context,
    Workflow,
    StartEvent,
    StopEvent,
    Event,
    step,
)
from .events import InitializeEvent, PDFIngestionEvent, ConciergeEvent, OrchestratorEvent, QueryEvent, QueryResultEvent


# workflow.py
from llama_index.core.workflow import Context, StartEvent, Workflow
from .steps import WorkflowSteps

class ConciergeWorkflow(Workflow):
    
    steps = WorkflowSteps()

    @step(pass_context=True)
    async def concierge(self, ctx: Context, ev: ConciergeEvent | StartEvent) -> InitializeEvent | OrchestratorEvent | None:
        return await self.steps.concierge(ctx, ev)

    @step(pass_context=True)
    async def initialize(self, ctx: Context, ev: InitializeEvent) -> OrchestratorEvent:
        return await self.steps.initialize(ctx, ev)

    @step(pass_context=True)
    async def orchestrator(self, ctx: Context, ev: OrchestratorEvent) -> ConciergeEvent | PDFIngestionEvent | QueryEvent | StopEvent:
        return await self.steps.orchestrator(ctx, ev)

    @step(pass_context=True)
    async def ingest(self, ctx: Context, ev: PDFIngestionEvent) -> InitializeEvent:
        return await self.steps.ingest(ctx, ev)
    
    @step(pass_context=True)
    async def query_index(self, ctx: Context, ev: QueryEvent) -> StopEvent:
        return await self.steps.query_index(ctx, ev)
