"""FastMCP Server implementation for Calculator MCP."""

import sys
import os
import argparse

# Ensure parent directory is in sys.path for module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mcp.server.fastmcp import FastMCP
from calculator_mcp.engine import (
    evaluate_expression,
    basic_arithmetic,
    scientific_calc,
    unit_convert,
    financial_calc,
    statistics_calc,
)

# Initialize FastMCP Server
mcp = FastMCP(
    "Calculator MCP Server",
    instructions="A Model Context Protocol server providing mathematical, financial, scientific, unit conversion, and statistical tools."
)


@mcp.tool()
def evaluate_math_expression(expression: str, precision: int = 10) -> str:
    """Evaluate complex mathematical expressions safely.
    
    Supports addition, subtraction, multiplication, division, exponents (^ or **),
    roots (sqrt, cbrt), trigonometric functions (sin, cos, tan), logarithms (log, log10, ln),
    and constants (pi, e).
    
    Args:
        expression: The mathematical expression string (e.g., '2 * (3 + 4)', 'sqrt(144) + sin(pi / 2)', '5^3')
        precision: Number of decimal digits of precision for symbolic evaluation (default 10)
    """
    res = evaluate_expression(expression, precision)
    if res.get("status") == "success":
        return f"Result: {res['result']} (Symbolic: {res['exact_symbolic']})"
    return f"Error: {res.get('error')}"


@mcp.tool()
def perform_arithmetic(operation: str, numbers: list[float]) -> str:
    """Perform basic arithmetic on a list of numbers.
    
    Args:
        operation: 'add', 'subtract', 'multiply', or 'divide'
        numbers: List of numbers to operate on in sequence
    """
    res = basic_arithmetic(operation, numbers)
    if res.get("status") == "success":
        return f"Result of {operation}: {res['result']}"
    return f"Error: {res.get('error')}"


@mcp.tool()
def scientific_calculation(operation: str, value: float, secondary_value: float | None = None) -> str:
    """Perform scientific mathematical calculations.
    
    Args:
        operation: 'power', 'sqrt', 'cbrt', 'factorial', 'sin', 'cos', 'tan', 'log', 'ln'
        value: Primary number input (for trig functions, value is in degrees if secondary_value is 1, else radians)
        secondary_value: Exponent for power, base for log, or 1 to indicate degree mode for trig functions
    """
    res = scientific_calc(operation, value, secondary_value)
    if res.get("status") == "success":
        return f"Result of {operation}: {res['result']}"
    return f"Error: {res.get('error')}"


@mcp.tool()
def convert_unit(value: float, from_unit: str, to_unit: str) -> str:
    """Convert quantities between physical units (length, weight/mass, temperature, volume, time).
    
    Examples:
    - convert_unit(100, "degC", "degF") -> Fahrenheit
    - convert_unit(5, "km", "miles") -> Miles
    - convert_unit(2, "hours", "sec") -> Seconds
    
    Args:
        value: Numerical value to convert
        from_unit: Source unit string (e.g., 'km', 'miles', 'kg', 'lbs', 'degC', 'degF', 'hr', 'sec')
        to_unit: Target unit string
    """
    res = unit_convert(value, from_unit, to_unit)
    if res.get("status") == "success":
        return f"{value} {from_unit} = {res['result']} {to_unit}"
    return f"Error: {res.get('error')}"


@mcp.tool()
def financial_calculator(
    calc_type: str,
    principal: float = 0.0,
    rate: float = 0.0,
    time: float = 0.0,
    compounding_frequency: int = 1,
    amount: float = 0.0
) -> str:
    """Calculate financial metrics like Simple Interest, Compound Interest, Loan EMI, and Percentages.
    
    Args:
        calc_type: 'simple_interest', 'compound_interest', 'loan_emi', or 'percentage'
        principal: Principal loan/investment amount (or base value for percentage)
        rate: Annual interest rate in percent (e.g., 7.5 for 7.5%)
        time: Duration in years
        compounding_frequency: Times per year compounding occurs (1=annual, 4=quarterly, 12=monthly)
        amount: Optional secondary parameter
    """
    res = financial_calc(calc_type, principal, rate, time, compounding_frequency, amount)
    if res.get("status") == "success":
        if calc_type in ("simple_interest", "compound_interest"):
            return f"Interest: {res['interest']} | Total Amount: {res['total_amount']}"
        elif calc_type == "loan_emi":
            return f"Monthly EMI: {res['monthly_emi']} | Total Interest: {res['total_interest']} | Total Payment: {res['total_payment']}"
        elif calc_type == "percentage":
            return f"Percentage Result: {res['result']}"
    return f"Error: {res.get('error')}"


@mcp.tool()
def calculate_statistics(operation: str, data: list[float]) -> str:
    """Calculate statistical summaries for a dataset of numbers.
    
    Args:
        operation: 'mean', 'median', 'mode', 'variance', 'stdev', or 'summary'
        data: List of numerical observations
    """
    res = statistics_calc(operation, data)
    if res.get("status") == "success":
        if operation == "summary":
            return f"Summary -> Count: {res['count']}, Sum: {res['sum']}, Min: {res['min']}, Max: {res['max']}, Mean: {res['mean']}, Median: {res['median']}, StDev: {res['stdev']}"
        return f"{operation.capitalize()}: {res['result']}"
    return f"Error: {res.get('error')}"


def main():
    parser = argparse.ArgumentParser(description="Calculator MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport mechanism: 'stdio' for Desktop/CLI apps or 'sse' for Web HTTP clients (default: stdio)",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host interface for SSE server (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port number for SSE server (default: 8000)",
    )
    args = parser.parse_args()

    if args.transport == "sse":
        print(f"Starting FastMCP Calculator Server in SSE mode on http://{args.host}:{args.port}/sse ...")
        mcp.settings.host = args.host
        mcp.settings.port = args.port
        mcp.run(transport="sse")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
