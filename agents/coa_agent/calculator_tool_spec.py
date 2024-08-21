from llama_index.core.tools.tool_spec.base import BaseToolSpec


class CalculatorToolSpec(BaseToolSpec):
    """Calculator tool spec."""
    spec_functions = ["multiply", "add", "subtract", "divide"]
    
    def divide(self, a: int, b: int) -> int:
        """Divide two integers and returns the result integer"""
        return a // b if b != 0 else 0

    def multiply(self, a: int, b: int) -> int:
        """Multiple two integers and returns the result integer"""
        return a * b

    def add(self, a: int, b: int) -> int:
        """Add two integers and returns the result integer"""
        return a + b

    def subtract(self, a: int, b: int) -> int:
        """Subtract two integers and returns the result integer"""
        return a - b