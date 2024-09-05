# tool_retriver.py

from typing import List, Optional, Dict
from llama_index.core.tools import BaseTool, AsyncBaseTool, FunctionTool
from llama_index.core.tools.types import adapt_to_async_tool
from .utils import json_schema_to_python

class ToolRetriever:
    """Class for retrieving tools based on specific queries or criteria."""

    def __init__(self, tools: Optional[List[BaseTool]] = None):
        """Initialize ToolRetriever with a list of tools."""
        self.tools = tools if tools is not None else []
        self.tool_retriever = None  # This can be set externally if needed

    def retrieve(self, query: str) -> List[AsyncBaseTool]:
        """
        Retrieve tools that are relevant to the given query.
        
        Args:
            query (str): The query to retrieve tools for.
            
        Returns:
            List[AsyncBaseTool]: A list of async tools that match the query.
        """
        if self.tool_retriever:
            # Use an external tool retriever if provided
            tools = self.tool_retriever.retrieve(query)
        else:
            # Default retrieval from internal tools list
            tools = self.tools
        
        # Convert tools to their async equivalent
        return [adapt_to_async_tool(tool) for tool in tools]


    def set_tool_retriever(self, retriever) -> None:
        """
        Set an external tool retriever.
        
        Args:
            retriever: An external tool retriever instance.
        """
        self.tool_retriever = retriever
        
        
    def prepare_tools(self, query: str) -> Dict[str, List]:
        """
        Prepare tools and generate their descriptions for use in a workflow step.
        
        Args:
            step (TaskStep): The current task step containing the input query.
            
        Returns:
            Dict[str, List]: A dictionary containing tools by name and tool descriptions.
        """
        # Retrieve tools based on the step input
        tools = self.retrieve(query)
        tools_by_name = {tool.metadata.name: tool for tool in tools}
        tools_strs = []
        
        for tool in tools:
            if isinstance(tool, FunctionTool):
                description = tool.metadata.description
                # Remove function definition, create custom description
                if "def " in description:
                    description = "\n".join(description.split("\n")[1:])
            else:
                description = tool.metadata.description

            tool_str = json_schema_to_python(
                tool.metadata.fn_schema_str, tool.metadata.name, description=description
            )
            tools_strs.append(tool_str)

        return {
            "tools_by_name": tools_by_name,
            "tools_strs": tools_strs
        }