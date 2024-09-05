
# workflow.py
from llama_index.core.workflow import Context, StartEvent, Workflow, StopEvent, step
from .events import InitializeEvent, FunctionCallEvent, ValidateFunctionCallEvent
from .prompts.evaluator import prometheus_relevancy_eval_prompt_template, prometheus_relevancy_refine_prompt_template
from .validator.relevancy_eval import GPT4RelevancyEvaluator
from .steps import FunctionCallSteps

class FunctionCallWorkflow(Workflow):
        
    steps = FunctionCallSteps()

    @step(pass_context=True)
    async def initialize_step(self, ctx: Context, ev: StartEvent | InitializeEvent) -> InitializeEvent | FunctionCallEvent | StopEvent:
        return await self.steps.initialize_step(ctx, ev)


    @step(pass_context=True)
    async def function_call_step(self, ctx: Context, ev: FunctionCallEvent) -> ValidateFunctionCallEvent | StopEvent:
        return await self.steps.function_call_step(ctx, ev)


    @step(pass_context=True)
    async def validate_function_step(self, ctx: Context, ev: ValidateFunctionCallEvent) -> FunctionCallEvent | StopEvent:
        return await self.steps.validate_function_step(ctx, ev)