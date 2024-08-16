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
from events import InitializeEvent, PDFIngestionEvent, ConciergeEvent, OrchestratorEvent, QueryEvent, QueryResultEvent
from orchestrator.ingestion.vector_store.pinecone.client import PineconeClient


from llama_index.core.workflow import Context, StartEvent, StopEvent

class WorkflowSteps:
    
    @step(pass_context=True)
    async def concierge(self, ctx: Context, ev: ConciergeEvent | StartEvent) -> InitializeEvent | OrchestratorEvent | None:
        if isinstance(ev, StartEvent):
            dirname = ev.get("dirname")
            if dirname is not None:
                ctx.data["dirname"] = dirname
                return OrchestratorEvent(request="ingest")  # Trigger the OrchestratorEvent for ingestion

            return InitializeEvent()

        # After initialization, direct to orchestrator for querying
        return OrchestratorEvent(request="query")

    @step(pass_context=True)
    async def initialize(self, ctx: Context, ev: InitializeEvent) -> OrchestratorEvent:
        ctx.data["index"] = PineconeClient(collection_name="pdf-docs").index
        return OrchestratorEvent(request="query")  # After initializing, direct to query

    @step(pass_context=True)
    async def orchestrator(self, ctx: Context, ev: OrchestratorEvent) -> QueryEvent | PDFIngestionEvent | StopEvent:
        if ev.request == "ingest":
            return PDFIngestionEvent(request="start_pdf_ingestion")
        
        elif ev.request == "query":
            return QueryEvent(query="how does Environmental difficulties at present are also challenging the sustainability?")
        
        return StopEvent(result={"message": "Orchestrator did not recognize the event"})

    @step(pass_context=True)
    async def query_index(self, ctx: Context, ev: QueryEvent) -> StopEvent:
        query_engine = ctx.data["index"].as_query_engine()
        response = query_engine.query(ev.query)
        return StopEvent(result={"query_result": str(response)})

    @step(pass_context=True)
    async def ingest(self, ctx: Context, ev: PDFIngestionEvent) -> InitializeEvent:
        dirname = ctx.data.get("dirname")
        if dirname:
            nodes = process_pdfs_in_directory(dirname)

            client = PineconeClient(collection_name="pdf-docs")
            client.upsert_indices(nodes)
            ctx.data["dirname"] = None
        return InitializeEvent()