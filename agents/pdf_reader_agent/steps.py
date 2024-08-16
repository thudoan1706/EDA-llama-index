from orchestrator.ingestion.vector_store.pinecone.client import PineconeClient
from llama_index.core.workflow import (
    Context,
    Workflow,
    StartEvent,
    StopEvent,
    Event,
    step,
)
import asyncio
from orchestrator.ingestion.utils.pdf_processor import process_pdfs_in_directory
from events import InitializeEvent, PDFIngestionEvent, ConciergeEvent, OrchestratorEvent
from orchestrator.ingestion.vector_store.pinecone.client import PineconeClient


from llama_index.core.workflow import Context, StartEvent, StopEvent

class WorkflowSteps:
    
    @step(pass_context=True)
    async def concierge(self, ctx: Context, ev: ConciergeEvent | StartEvent) -> InitializeEvent | StopEvent | OrchestratorEvent | None:
        if isinstance(ev, StartEvent):
            dirname = ev.get("dirname")
            if dirname is not None:
                ctx.data["dirname"] = dirname
                return OrchestratorEvent(request="ingest")  # Trigger the OrchestratorEvent for ingestion

            return InitializeEvent()

        return StopEvent(result={"index": ctx.data["index"]})

    @step(pass_context=True)
    async def initialize(self, ctx: Context, ev: InitializeEvent) -> ConciergeEvent:
        ctx.data["index"] = PineconeClient(collection_name="pdf-docs")
        return ConciergeEvent()
    
    @step(pass_context=True)
    async def orchestrator(self, ctx: Context, ev: OrchestratorEvent) -> ConciergeEvent | PDFIngestionEvent | StopEvent:
        if ev.request == "ingest":
            return PDFIngestionEvent(request="start_pdf_ingestion")
        return StopEvent(result={"message": "Orchestrator did not recognize the event"})

    @step(pass_context=True)
    async def ingest(self, ctx: Context, ev: PDFIngestionEvent) -> InitializeEvent | None:
        dirname = ctx.data.get("dirname")
        if dirname:
            nodes = process_pdfs_in_directory(dirname)

            client = PineconeClient(collection_name="pdf-docs")
            client.upsert_indices(nodes)
            ctx.data["dirname"] = None
            return InitializeEvent()
        return None
