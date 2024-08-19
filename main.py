import asyncio
from agents.pdf_reader_agent.workflow import ConciergeWorkflow

async def main():
    concierge = ConciergeWorkflow(timeout=180, verbose=True)
    dirname = "agents/pdf_reader_agent/orchestrator/ingestion/data"
    
    # Provide dirname if we want to ingest pdf files to pinecone
    # result = await concierge.run(dirname=dirname)
    while True:
        result = await concierge.run()
        print("Workflow Final Result:", result["query_result"])
    
    # from llama_index.utils.workflow import (
    #     draw_all_possible_flows,
    #     draw_most_recent_execution,
    # )
    # draw_all_possible_flows(ConciergeWorkflow, filename="./diagrams/workflow_all.html")
    # draw_most_recent_execution(concierge, filename="./diagrams/workflow_recent.html")
    
    # print("Workflow Final Result:", result["query_result"])

# Execute the main function using asyncio
if __name__ == "__main__":
    
    asyncio.run(main())