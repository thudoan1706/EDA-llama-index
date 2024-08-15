from ingestion.vector_store.pinecone.client import PineconeClient
from llama_index.core.workflow import (
    Context,
    Workflow,
    StartEvent,
    StopEvent,
    Event,
    step,
)
import asyncio
from ingestion.utils.pdf_processor import process_pdfs_in_directory
from event import InitializeEvent, PDFIngestionEvent, ConciergeEvent
from ingestion.vector_store.pinecone.client import PineconeClient


class ConciergeWorkflow(Workflow):
    @step(pass_context=True)
    async def concierge(self, ctx: Context, ev: ConciergeEvent | StartEvent) -> InitializeEvent | StopEvent | None:
    
        if isinstance(ev, StartEvent):
            dirname = ev.get("dirname")
            if dirname is not None:
                ctx.data["dirname"] = dirname
                
            return InitializeEvent()
        
        return StopEvent(result={"index": ctx.data["index"]})
    
    @step(pass_context=True)
    async def initialize(self, ctx: Context, ev: InitializeEvent) -> PDFIngestionEvent | ConciergeEvent:
        # Check if "dirname" exists in ctx.data and is not None
        if ctx.data.get("dirname") is not None:
            return PDFIngestionEvent(dirname=ctx.data["dirname"])
        
        ctx.data["index"] = PineconeClient(collection_name="pdf-docs")
        return ConciergeEvent()
    
    @step(pass_context=True)
    async def ingest(self, ctx: Context, ev: PDFIngestionEvent) -> InitializeEvent | None:
        """Entry point to ingest a document, triggered by a StartEvent with `dirname`."""
        dirname = ctx.data.get("dirname")
        if dirname:
            nodes = process_pdfs_in_directory(dirname)

            client = PineconeClient(collection_name="pdf-docs")
            client.upsert_indices(nodes)
            ctx.data["dirname"] = None
            return InitializeEvent()
        return None


async def main():
    concierge = ConciergeWorkflow(timeout=180, verbose=True)
    result = await concierge.run()
    query_engine = result["index"].index.as_query_engine()
    response = query_engine.query("how does Environmental difficulties at present are also challenging the sustainability of the Mediterranean way of living")
    # from llama_index.utils.workflow import (
    #     draw_all_possible_flows,
    #     draw_most_recent_execution,
    # )
    # draw_all_possible_flows(ConciergeWorkflow, filename="./diagrams/workflow_all.html")
    # draw_most_recent_execution(concierge, filename="./diagrams/workflow_recent.html")
    
    print("Workflow Final Result:", response)

# Execute the main function using asyncio
if __name__ == "__main__":
    asyncio.run(main())