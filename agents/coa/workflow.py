# workflow.py
from llama_index.core.workflow import Context, StartEvent, Workflow, StopEvent, step
from .events import InitializeEvent, FunctionCallEvent, ValidateFunctionCallEvent, StepGeneratorEvent, EvaluateFunctionEvent
from .prompts.evaluator import prometheus_relevancy_eval_prompt_template, prometheus_relevancy_refine_prompt_template
from .validator.relevancy_eval import GPT4RelevancyEvaluator
from .steps import FunctionCallSteps
from .step_generator import StepGenerator

class ChainOfAbstractionWorkflow(Workflow):

    steps = ChainOfAbstractionSteps()

    def __init__(self):
        super().__init__()
        self.step_generator = StepGenerator()

    @step(pass_context=True)
    async def initialize_step(self, ctx: Context, ev: StartEvent | InitializeEvent) -> InitializeEvent | FunctionCallEvent | StopEvent:
        """Initialize the workflow context and decide initial reasoning."""
        return await self.steps.initialize_step(ctx, ev)

    @step(pass_context=True)
    async def initial_reasoning_step(self, ctx: Context, ev: FunctionCallEvent) -> FunctionCallEvent | StopEvent:
        """Generate initial reasoning to decide the first function call."""
        return await self.steps.initial_reasoning_step(ctx, ev)

    @step(pass_context=True)
    async def function_call_step(self, ctx: Context, ev: FunctionCallEvent) -> ValidateFunctionCallEvent | StopEvent:
        """Execute the function based on the current plan."""
        return await self.steps.function_call_step(ctx, ev)

    @step(pass_context=True)
    async def validate_function_step(self, ctx: Context, ev: ValidateFunctionCallEvent) -> EvaluateFunctionEvent | StopEvent:
        """Validate the function output and prepare for evaluation."""
        return await self.steps.validate_function_step(ctx, ev)

    @step(pass_context=True)
    async def evaluate_function_step(self, ctx: Context, ev: EvaluateFunctionEvent) -> StepGeneratorEvent | StopEvent:
        """Evaluate the validated function output to decide the next step."""
        evaluation_result = await self.steps.evaluate_function_step(ctx, ev)
        return StepGeneratorEvent(evaluation_result=evaluation_result)

    @step(pass_context=True)
    async def step_generator(self, ctx: Context, ev: StepGeneratorEvent) -> FunctionCallEvent | StopEvent:
        """Generate the next step based on the evaluation result."""
        return await self.step_generator.generate_next_steps(ctx, ev)
