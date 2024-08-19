from .orchestrator.ingestion.vector_store.pinecone.client import PineconeClient
from llama_index.core.workflow import (
    Context,
    Workflow,
    StartEvent,
    StopEvent,
    Event,
    step,
)
from .orchestrator.utils.pdf_processor import process_pdfs_in_directory
from .events import InitializeEvent, PDFIngestionEvent, ConciergeEvent, OrchestratorEvent, QueryEvent, QueryResultEvent
from .orchestrator.ingestion.vector_store.pinecone.client import PineconeClient
from llama_index.core.workflow import Context, StartEvent, StopEvent
import time
from llama_index.core import get_response_synthesizer
from .orchestrator.rag.query_engine import QueryEngine
import os
os.environ["OPENAI_API_KEY"] = ""
class WorkflowSteps:
    
    @step(pass_context=True)
    async def concierge(self, ctx: Context, ev: ConciergeEvent | StartEvent) -> InitializeEvent | OrchestratorEvent | None:
        if isinstance(ev, StartEvent):
            dirname = ev.get("dirname")
            if dirname is not None:
                ctx.data["dirname"] = dirname
                return OrchestratorEvent(request="ingest")

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
        
            user_input = input("Ask any questions you have regarding diet: ")
            # self.send_event(QueryEvent(query=user_input))
            return QueryEvent(query=user_input)
        
        return StopEvent(result={"message": "Orchestrator did not recognize the event"})

    @step(pass_context=True)
    async def ingest(self, ctx: Context, ev: PDFIngestionEvent) -> InitializeEvent:
        dirname = ctx.data.get("dirname")
        if dirname:
            nodes = process_pdfs_in_directory(dirname)

            client = PineconeClient(collection_name="pdf-docs")
            client.upsert_indices(nodes)
            time.sleep(3)
            ctx.data["dirname"] = None
        return InitializeEvent()
    
    
    @step(pass_context=True)
    async def query_index(self, ctx: Context, ev: QueryEvent) -> StopEvent:
        retriever = ctx.data["index"].as_retriever()
        synthesizer = get_response_synthesizer(response_mode="compact")
        query_engine = QueryEngine(
            retriever=retriever, response_synthesizer=synthesizer
        )
        response = query_engine.query(ev.query)
        print("len source nodes", len(response.source_nodes))
        print(response.source_nodes[0].get_content())

        return StopEvent(result={"query_result": str(response), "source_node": response.source_nodes[0].get_content()})