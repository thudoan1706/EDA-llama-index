import asyncio
from agents.pdf_reader_agent.workflow import ConciergeWorkflow
import os
os.environ["OPENAI_API_KEY"] = ""

async def main():
    concierge = ConciergeWorkflow(timeout=180, verbose=True)
    dirname = "agents/pdf_reader_agent/orchestrator/ingestion/data/diet"
    
    # Provide dirname if we want to ingest pdf files to pinecone
    result = await concierge.run(query="what knowledge do you have", dirname=dirname, collection_name="pdf-diet-docs")
    print(result)
    #     result = await concierge.run(query='hello', dirname=dirname)
    #     print("Workflow Final Result:", result)
    
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