from llama_index.core.tools import QueryEngineTool
from llama_index.core.evaluation import RelevancyEvaluator
from llama_index.core import Settings
from llama_index.core.schema import NodeWithScore
from typing import Any, List, Dict
from llama_index.llms.openai import OpenAI
import os
from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI
from .custom_relevancy import CustomRelevancyEvaluator

os.environ["OPENAI_API_KEY"] = ""
class GPT4RelevancyEvaluator:
    """Class for GPT-4 Relevancy Evaluation."""
    
    def __init__(self, eval_template: str, refine_template: str):
        # Initialize GPT-4 model and relevancy evaluator
        gpt4o = OpenAI(temperature=0, model="gpt-4o")
        
        
        HF_TOKEN = ""
        HF_ENDPOINT_URL = (
        )

        prometheus_llm = HuggingFaceInferenceAPI(
        model_name=HF_ENDPOINT_URL,
        token=HF_TOKEN,
        temperature=0.1,
        do_sample=True,
        top_p=0.95,
        top_k=40,
        repetition_penalty=1.1,
        )
        
        Settings.llm = gpt4o
        
        self.relevancy_evaluator = CustomRelevancyEvaluator(
            eval_template=eval_template,
            refine_template=refine_template,
        )
        

    def evaluate_sources(self, query_str: str, response_vector: Any) -> List[Any]:
        """Evaluate relevancy for all source nodes in the response vector and return only 'Pass' nodes."""
        eval_source_result_full = [
            self.relevancy_evaluator.evaluate(
                query=query_str,
                response=None,
                contexts=[source_node],
            )
            for source_node in response_vector["source_node"]
        ]
        
        for eval in eval_source_result_full:
            print(eval.feedback)

        # Filter and return only the original source nodes where the evaluation passed
        pass_nodes = [
            source_node for result, source_node in zip(eval_source_result_full, response_vector["source_node"]) if result.passing
        ]
        
        print("Number of nodes before validated ", len(response_vector["source_node"]))
        print("Number of nodes after validated ", len(pass_nodes))
        gpt4o = OpenAI(temperature=0, model="gpt-4o")
        Settings.llm = gpt4o
        
        if len(pass_nodes) == 0:
            pass_nodes = ["No output is generated. Please modify the input for the current function call"]
        return pass_nodes, len(pass_nodes)