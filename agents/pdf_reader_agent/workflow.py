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


# workflow.py
from llama_index.core.workflow import Context, StartEvent, Workflow
from steps import WorkflowSteps

class ConciergeWorkflow(Workflow):
    
    steps = WorkflowSteps()

    @step(pass_context=True)
    async def concierge(self, ctx: Context, ev: ConciergeEvent | StartEvent) -> InitializeEvent | StopEvent | OrchestratorEvent | None:
        return await self.steps.concierge(ctx, ev)

    @step(pass_context=True)
    async def initialize(self, ctx: Context, ev: InitializeEvent) -> ConciergeEvent:
        return await self.steps.initialize(ctx, ev)

    @step(pass_context=True)
    async def orchestrator(self, ctx: Context, ev: OrchestratorEvent) -> ConciergeEvent | PDFIngestionEvent | StopEvent:
        return await self.steps.orchestrator(ctx, ev)

    @step(pass_context=True)
    async def ingest(self, ctx: Context, ev: PDFIngestionEvent) -> InitializeEvent | None:
        return await self.steps.ingest(ctx, ev)



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