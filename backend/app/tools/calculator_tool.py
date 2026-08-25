"""
ManufacturingAgent Safe Engineering Calculator Tool
Performs safe, bounded mathematical calculations for manufacturing telemetry evaluations.
"""

import math
import re
from typing import Dict, Any, Union
from pydantic import BaseModel, Field


class CalculatorInput(BaseModel):
    expression: str = Field(description="Mathematical expression to evaluate, e.g. '(85.2 - 68.0) / 68.0 * 100'")


class CalculatorResult(BaseModel):
    success: bool
    expression: str
    result: Union[float, int, str, None]
    error: Union[str, None] = None


# Allowed safe symbols and functions
SAFE_MATH = {
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "sum": sum,
    "sqrt": math.sqrt,
    "pow": math.pow,
    "log": math.log,
    "exp": math.exp,
    "pi": math.pi,
    "e": math.e
}


def calculate(expression: str) -> Dict[str, Any]:
    """
    Safely evaluate arithmetic and engineering expressions.
    Guards against arbitrary code execution by strictly sanitizing input.
    """
    if not expression or not expression.strip():
        return {
            "success": False,
            "expression": expression,
            "result": None,
            "error": "Expression cannot be empty."
        }

    clean_expr = expression.strip()

    # Block any dangerous keywords, dunders, or builtins
    disallowed_patterns = [
        r'__', r'import', r'eval', r'exec', r'globals', r'locals',
        r'open', r'os', r'sys', r'subprocess', r'class', r'lambda'
    ]
    for pat in disallowed_patterns:
        if re.search(pat, clean_expr, re.IGNORECASE):
            return {
                "success": False,
                "expression": clean_expr,
                "result": None,
                "error": f"Disallowed keyword or pattern '{pat}' in expression."
            }

    # Only allow digits, basic operators, commas, parentheses, dots, spaces, and whitelisted math function names
    allowed_chars = set("0123456789+-*/%()., eE_")
    non_math_tokens = re.findall(r'[a-zA-Z_]+', clean_expr)
    for tok in non_math_tokens:
        if tok not in SAFE_MATH:
            return {
                "success": False,
                "expression": clean_expr,
                "result": None,
                "error": f"Unauthorized symbol or function '{tok}' in calculation."
            }

    try:
        # Evaluate in isolated namespace
        result = eval(clean_expr, {"__builtins__": {}}, SAFE_MATH)
        if isinstance(result, (int, float)):
            # Check for infinity or NaN
            if math.isnan(result) or math.isinf(result):
                return {
                    "success": False,
                    "expression": clean_expr,
                    "result": str(result),
                    "error": "Calculation resulted in non-finite value (NaN or Inf)."
                }
            rounded_result = round(result, 6) if isinstance(result, float) else result
            return {
                "success": True,
                "expression": clean_expr,
                "result": rounded_result,
                "error": None
            }
        else:
            return {
                "success": True,
                "expression": clean_expr,
                "result": str(result),
                "error": None
            }
    except ZeroDivisionError:
        return {
            "success": False,
            "expression": clean_expr,
            "result": None,
            "error": "Division by zero."
        }
    except Exception as e:
        return {
            "success": False,
            "expression": clean_expr,
            "result": None,
            "error": f"Evaluation error: {str(e)}"
        }
