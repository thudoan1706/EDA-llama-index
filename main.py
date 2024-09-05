

import asyncio
from typing import Dict
from pydantic import BaseModel, Field
from agents.pdf_reader_agent.workflow import ConciergeWorkflow as DietConsultantAgent, ConciergeWorkflow as NutritionConsultantAgent
from llama_index.core.tools import FunctionTool
from llama_index.agent.openai import OpenAIAgent
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings
from agents.coa_agent.output_parser.custom import ChainOfAbstractionParser
from llama_index.packs.agents_coa import CoAAgentPack, CoAAgentWorker
import os
from agents.coa_agent.prompts.refining import REFINE_REASONING_PROMPT_TEMPLATE



# Define a Pydantic model for input validation
class DietQuery(BaseModel):
    query: str = Field(description="A question or query related to diet.")

# Asynchronous function with Pydantic validation
async def consult_diet_async(query: str) -> Dict[str, str]:
    concierge = DietConsultantAgent(timeout=180, verbose=True)
    result = await concierge.run(query=query, collection_name="pdf-diet-docs")
    return result

# Synchronous wrapper for the asynchronous function with Pydantic validation
def consult_diet(query: str) -> Dict[str, object]:
    # Validate the input using the Pydantic model
    input_data = DietQuery(query=query)
    # Run the asynchronous function
    return asyncio.run(consult_diet_async(input_data.query))


# Define a Pydantic model for input validation with the updated class name
class NutritionQuery(BaseModel):
    query: str = Field(description="A question or query related to nutrition.")

# Asynchronous function with Pydantic validation and updated collection name
async def consult_nutrition_async(query: str) -> Dict[str, str]:
    concierge = NutritionConsultantAgent(timeout=180, verbose=True)
    result = await concierge.run(query=query, collection_name="pdf-nutrition-docs")
    return result

# Synchronous wrapper for the asynchronous function with Pydantic validation
def consult_nutrition(query: str) -> Dict[str, object]:
    # Validate the input using the updated Pydantic model
    input_data = NutritionQuery(query=query)
    # Run the asynchronous function
    return asyncio.run(consult_nutrition_async(input_data.query))


def main():
    # Create the FunctionTool for diet consultation with the synchronous wrapper
    diet_tool = FunctionTool.from_defaults(
        fn=consult_diet,
        name="consult_diet",
        description="Consults on diet based on a query.",
    )

    # Create the FunctionTool for nutrition consultation with the synchronous wrapper
    nutrition_tool = FunctionTool.from_defaults(
        fn=consult_nutrition,
        name="consult_nutrition",
        description="Provides nutritional information based on a query.",
    )

    # Initialize OpenAI with GPT-4 model (or other desired model)
    gpt4o = OpenAI(temperature=0, model="gpt-4o")
    Settings.llm = gpt4o

    # Initialize the COA Agent Worker with both tools
    worker = CoAAgentWorker.from_tools(
        refine_reasoning_prompt_template=REFINE_REASONING_PROMPT_TEMPLATE,
        output_parser=ChainOfAbstractionParser(),
        tools=[diet_tool, nutrition_tool],
        verbose=True,
    )

    # Create an agent from the worker
    agent = worker.as_agent()

    # Run the agent with a specific query that involves both tools
    # query = (
    #     "How do omega-3 fatty acids found in fish impact brain health, and what are the recommended dietary guidelines "
    #     "for incorporating fish into a Mediterranean diet to maximize cognitive benefits? "
    #     "Please include both the nutritional science behind omega-3s and practical meal planning tips."
    #     "What is the Indo-Mediterranean diet"
    # )
    
    query = (
        "How do omega-3 fatty acids found in fish impact brain health, and what are the recommended dietary guidelines "
        "for incorporating fish into a Mediterranean diet to maximize cognitive benefits? "
        "Please include both the nutritional science behind omega-3s and practical meal planning tips."
        "What is the Indo-Mediterranean diet"
    )
    response = agent.chat(query)
    print(response)

# Entry point for the script
if __name__ == "__main__":
    main()