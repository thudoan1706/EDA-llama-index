# workflow.py
from llama_index.core.workflow import Context, StartEvent, Workflow, StopEvent, step
from .events import InitializeEvent, FunctionCallEvent, ValidateFunctionCallEvent
from .prompts.evaluator import prometheus_relevancy_eval_prompt_template, prometheus_relevancy_refine_prompt_template
from .validator.relevancy_eval import GPT4RelevancyEvaluator
from typing import List, Any

class FunctionCallSteps:
    def __init__(self, max_num_sources = 3):
        self.max_num_sources = max_num_sources
        evaluator = GPT4RelevancyEvaluator(prometheus_relevancy_eval_prompt_template, prometheus_relevancy_refine_prompt_template)

        self.validator = evaluator
        
    @step(pass_context=True)
    async def initialize_step(self, ctx: Context, ev: StartEvent | InitializeEvent) -> InitializeEvent | FunctionCallEvent | StopEvent:
        """Initialize the workflow context."""
        if isinstance(ev, StartEvent):
            # Perform initial setup, e.g., load tools, validators, etc.
            ctx.data["results"] = {}
            ctx.data["tools_by_name"] = ev.tools_by_name
            ctx.data["function_calls"] = ev.func_calls
            ctx.data["iteration"] = 0
            ctx.data["accumulated_sources"] = 0

            # Produce an InitializeEvent to start initialization
            return InitializeEvent()

        # After initialization, check if there are function calls to process
        if ctx.data["function_calls"]:
            first_func_call = ctx.data["function_calls"][0]
            return FunctionCallEvent(func_call=first_func_call)
        else:
            return StopEvent({"message": "No function calls to process.", "results": ctx.data["results"]})

    @step(pass_context=True)
    async def function_call_step(self, ctx: Context, ev: FunctionCallEvent) -> ValidateFunctionCallEvent | StopEvent:
        """Execute a function call and prepare for validation."""
        func_name, raw_inputs, output_placeholder = ev.func_call
        input_data = self._prepare_inputs(ctx, raw_inputs)

        try:
            tool_output = await ctx.data["tools_by_name"][func_name].acall(*input_data)
            
            # print(f"Executed {func_name} with inputs {input_data} -> {output_placeholder}: {tool_output} \n")
        except Exception as e:
            error_message = f"Error in {func_name} with inputs {input_data}: {str(e)}"
            print(error_message)  # Log error for debugging
            return self._handle_error(error_message)

        
        if self.validator:
            return ValidateFunctionCallEvent(
                input_data=input_data + [tool_output.raw_output],
                output_placeholder=output_placeholder,
                tool_output=tool_output
            )


        ctx.data["results"][output_placeholder] = tool_output.content
        return await self._move_to_next_function(ctx)

    def _prepare_inputs(self, ctx: Context, raw_inputs: str) -> List[Any]:
        """Parse and prepare function inputs."""
        results = ctx.data["results"]
        input_data = []
        for raw_input in raw_inputs.split(","):
            raw_input = raw_input.strip()
            try:
                input_data.append(int(results.get(raw_input, raw_input)))
            except ValueError:
                input_data.append(raw_input)  # Handle non-integer inputs gracefully
        return input_data

    @step(pass_context=True)
    async def validate_function_step(self, ctx: Context, ev: ValidateFunctionCallEvent) -> FunctionCallEvent | StopEvent:
        """Validate function output and decide on the next step."""
        try:
            validator_output = self.validator.evaluate_sources(*ev.input_data)
            # print(f"Validation result: {validator_output} | Tool output: {ev.tool_output}")
        except Exception as e:
            return self._handle_error(f"Validation error: {e}")

        if validator_output:
            
            source_nodes, length_nodes = validator_output
            
            if length_nodes > 0:
                ctx.data["results"][ev.output_placeholder] = str(source_nodes)
                # Accumulate source if validation is successful
                ctx.data["accumulated_sources"] += length_nodes

                # Check if the maximum number of sources has been accumulated
                if ctx.data["accumulated_sources"] >= self.max_num_sources:
                    return StopEvent({"message": "Maximum number of sources accumulated.", "results": ctx.data["results"]})

            return await self._move_to_next_function(ctx)

        return self._handle_error("Tool output does not match the expected validation result")

    async def _move_to_next_function(self, ctx: Context) -> FunctionCallEvent | StopEvent:
        """Move to the next function call if available."""
        iteration = ctx.data["iteration"]
        function_calls = ctx.data["function_calls"]

        if iteration + 1 < len(function_calls):
            ctx.data["iteration"] += 1
            next_func_call = function_calls[ctx.data["iteration"]]
            return FunctionCallEvent(func_call=next_func_call)

        # End of the workflow, produce a StopEvent
        return StopEvent({"message": "All function calls processed.", "results": ctx.data["results"]})

    def _handle_error(self, message: str) -> StopEvent:
        """Handle errors gracefully and provide feedback."""
        return StopEvent({"message": message, "results": {}})