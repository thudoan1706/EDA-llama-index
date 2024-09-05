import nest_asyncio
import asyncio
import re
from typing import Dict, Tuple, List
from agents.coa_agent.workflow import FunctionCallWorkflow
from llama_index.core.tools import AsyncBaseTool, ToolOutput
from llama_index.core.types import BaseOutputParser
from llama_index.core.workflow import Context

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

class ChainOfAbstractionParser(BaseOutputParser):
    """Chain of abstraction output parser."""

    def __init__(self, verbose: bool = False):
        """Initialize the parser with verbosity and workflow setup."""
        self._verbose = verbose

    def parse(
        self, solution: str, tools_by_name: Dict[str, AsyncBaseTool]
    ) -> Tuple[str, List[ToolOutput]]:
        """Run the async parse method, handling running event loops."""
        if asyncio.get_event_loop().is_running():
            # Use `await` if inside a running event loop (Jupyter Notebook case)
            return asyncio.get_event_loop().run_until_complete(self.aparse(solution, tools_by_name))
        else:
            # Normal use case outside of Jupyter, use asyncio.run
            return asyncio.run(self.aparse(solution, tools_by_name))

    async def aparse(
        self, solution: str, tools_by_name: Dict[str, AsyncBaseTool]
    ) -> Tuple[str, List[ToolOutput]]:
        """Asynchronously parse the solution and execute the workflow."""
        # Extract function calls
        func_calls = re.findall(r"\[FUNC (\w+)\((.*?)\) = (\w+)\]", solution)
        # Initialize the workflow
        workflow = FunctionCallWorkflow(timeout=60)
        # Run the workflow
        response = await workflow.run(timeout=60,tools_by_name=tools_by_name, func_calls=func_calls)
        
        results = response["results"]
        # print(context.data)

        # Collect results from the workflow
        tool_outputs = []
        for func_name, raw_inputs, output_placeholder in func_calls:
            if output_placeholder in results:
                tool_outputs.append(
                    ToolOutput(
                        content=results[output_placeholder],
                        tool_name=func_name,
                        raw_output=results[output_placeholder],
                        raw_input={"args": raw_inputs},
                        is_error=False,
                    )
                )
            else:
                tool_outputs.append(
                    ToolOutput(
                        content="Error: No output generated.",
                        tool_name=func_name,
                        raw_output=None,
                        raw_input={"args": raw_inputs},
                        is_error=True,
                    )
                )


        # Replace placeholders in the solution text
        for placeholder, value in results.items():
            solution = solution.replace(f"{placeholder}", '"' + str(value) + '"')
            print("\n")

        return solution, tool_outputs