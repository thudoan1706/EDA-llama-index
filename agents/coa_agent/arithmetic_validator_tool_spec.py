from llama_index.core.tools.tool_spec.base import BaseToolSpec
from typing import List

operation_mapper = {
    "add": "+",
    "subtract": "-",
    "divide": "/",
    "multiply": "*"
}


def create_expression(num1:int, num2: int, operation_namespace: str):
    return f"{str(num1)} {operation_mapper[operation_namespace]} {str(num2)}"
    

class ArithmeticValidatorToolSpec(BaseToolSpec):
    """ Tool to eval the result of Calculator tool"""
    spec_functions = ["eval_expression"]
    
    def eval_expression(self, num1: int, num2: int, operation_namespace: str ) -> int:
        """
        Evaluate the given arithmetic expression and return the result.

        This method supports the following operations:
        - Addition (+)
        - Subtraction (-)
        - Multiplication (*)
        - Division (/)
        - Parentheses for grouping expressions ()

        :param expression: A string containing the arithmetic expression to evaluate.
                           The expression should be a valid mathematical expression
                           containing integers and the operators +, -, *, /, and ().
        :return: The result of evaluating the arithmetic expression as an integer.
=
        Example:
            calculator = ArithmeticCalculator()
            result = calculator.calculate("3+(2*2)")
            print(result)  # Output: 7
        """
        
        expression = create_expression(num1, num2, operation_namespace)
        
        num = 0
        op = "+"
        stack = []

        def helper(op, num):
            if op == "+":
                stack.append(num)
            elif op == "-":
                stack.append(-num)
            elif op == "*":
                stack.append(stack.pop() * num)
            elif op == "/":
                stack.append(int(stack.pop() / num))

        for i, char in enumerate(expression):
            if char.isdigit():
                num = num * 10 + int(char)
            elif char == '(':
                stack.append(op)
                num = 0
                op = "+"
            elif char in '+-*/)' or i == len(expression) - 1:
                helper(op, num)

                if char == ")":
                    num = 0
                    while isinstance(stack[-1], int):
                        num += stack.pop()
                    op = stack.pop()
                    helper(op, num)

                num = 0
                op = char
        helper(op, num)

        return sum(stack)
