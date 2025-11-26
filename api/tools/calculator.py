"""Calculator tool for arithmetic calculations."""

from pydantic import BaseModel, Field
from typing import Literal

from langchain.tools import tool


class CalculatorInput(BaseModel):
    expression: str = Field(..., description="The mathematical expression to evaluate")


@tool(
    "calculator",
    description="Performs arithmetic calculations. Use this for any math problems.",
    args_schema=CalculatorInput,
)
def calculator_tool(input: CalculatorInput) -> str:
    """Evaluate mathematical expressions."""
    return str(eval(input.expression))
