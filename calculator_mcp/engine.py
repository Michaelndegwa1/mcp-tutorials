"""Core mathematical evaluation engine for Calculator MCP Server."""

import math
import statistics
from typing import Any, Dict, List, Union
import sympy


def evaluate_expression(expression: str, precision: int = 10) -> Dict[str, Any]:
    """Safely evaluate a mathematical expression using SymPy.
    
    Supports variables like pi, e, trig functions, powers, logarithms, roots, etc.
    Examples: '2 * (3 + 4)', 'sqrt(144) + sin(pi / 2)', 'log(100, 10)', '5^2'
    """
    try:
        # Pre-process expression for common user shorthands
        cleaned_expr = expression.replace("^", "**")
        
        # Define allowed safe transformations & symbols
        local_dict = {
            "pi": sympy.pi,
            "e": sympy.E,
            "sin": sympy.sin,
            "cos": sympy.cos,
            "tan": sympy.tan,
            "asin": sympy.asin,
            "acos": sympy.acos,
            "atan": sympy.atan,
            "sqrt": sympy.sqrt,
            "cbrt": lambda x: sympy.Pow(x, sympy.Rational(1, 3)),
            "log": lambda x, base=sympy.E: sympy.log(x, base),
            "log10": lambda x: sympy.log(x, 10),
            "ln": sympy.log,
            "exp": sympy.exp,
            "factorial": sympy.factorial,
            "abs": sympy.Abs,
            "deg2rad": lambda deg: deg * sympy.pi / 180,
            "rad2deg": lambda rad: rad * 180 / sympy.pi,
        }
        
        parsed = sympy.parse_expr(cleaned_expr, local_dict=local_dict, transformations="all")
        numerical_result = parsed.evalf(precision)
        
        # Check if numerical result can be simplified to float/int
        if numerical_result.is_real:
            val = float(numerical_result)
            # If it's an integer value, round neatly
            if val.is_integer():
                val = int(val)
        else:
            val = str(numerical_result)
            
        return {
            "expression": expression,
            "exact_symbolic": str(parsed),
            "result": val,
            "status": "success"
        }
    except Exception as err:
        return {
            "expression": expression,
            "error": str(err),
            "status": "error"
        }


def basic_arithmetic(operation: str, numbers: List[float]) -> Dict[str, Any]:
    """Perform basic arithmetic operations on a list of numbers."""
    if not numbers:
        return {"status": "error", "error": "Number list cannot be empty"}
        
    op = operation.lower().strip()
    try:
        if op in ("add", "sum", "+"):
            result = sum(numbers)
        elif op in ("subtract", "minus", "-"):
            result = numbers[0] - sum(numbers[1:])
        elif op in ("multiply", "product", "*"):
            result = 1.0
            for n in numbers:
                result *= n
        elif op in ("divide", "quotient", "/"):
            result = numbers[0]
            for n in numbers[1:]:
                if n == 0:
                    return {"status": "error", "error": "Division by zero encountered"}
                result /= n
        else:
            return {"status": "error", "error": f"Unsupported operation: {operation}"}
            
        # Format integer if applicable
        if isinstance(result, float) and result.is_integer():
            result = int(result)
            
        return {
            "operation": operation,
            "numbers": numbers,
            "result": result,
            "status": "success"
        }
    except Exception as err:
        return {"status": "error", "error": str(err)}


def scientific_calc(operation: str, value: float, secondary_value: Union[float, None] = None) -> Dict[str, Any]:
    """Perform single or two-operand scientific calculation."""
    op = operation.lower().strip()
    try:
        if op == "power":
            if secondary_value is None:
                return {"status": "error", "error": "secondary_value (exponent) is required for power"}
            res = math.pow(value, secondary_value)
        elif op in ("sqrt", "square_root"):
            if value < 0:
                return {"status": "error", "error": "Cannot compute real square root of a negative number"}
            res = math.sqrt(value)
        elif op in ("cbrt", "cube_root"):
            res = math.cbrt(value)
        elif op == "factorial":
            if value < 0 or not float(value).is_integer():
                return {"status": "error", "error": "Factorial requires a non-negative integer"}
            res = math.factorial(int(value))
        elif op == "sin":
            res = math.sin(math.radians(value)) if secondary_value == 1 else math.sin(value)
        elif op == "cos":
            res = math.cos(math.radians(value)) if secondary_value == 1 else math.cos(value)
        elif op == "tan":
            res = math.tan(math.radians(value)) if secondary_value == 1 else math.tan(value)
        elif op == "log":
            base = secondary_value if secondary_value is not None else 10
            res = math.log(value, base)
        elif op == "ln":
            res = math.log(value)
        else:
            return {"status": "error", "error": f"Unknown scientific operation: {operation}"}
            
        if isinstance(res, float):
            res = round(res, 10)
            if res.is_integer():
                res = int(res)
            
        return {
            "operation": operation,
            "value": value,
            "secondary_value": secondary_value,
            "result": res,
            "status": "success"
        }
    except Exception as err:
        return {"status": "error", "error": str(err)}


# Predefined conversion rates relative to standard base units
CONVERSION_TABLE = {
    "length": {  # Base: meter
        "m": 1.0, "meter": 1.0, "meters": 1.0,
        "km": 1000.0, "kilometer": 1000.0, "kilometers": 1000.0,
        "cm": 0.01, "centimeter": 0.01, "centimeters": 0.01,
        "mm": 0.001, "millimeter": 0.001, "millimeters": 0.001,
        "mile": 1609.344, "miles": 1609.344,
        "yard": 0.9144, "yards": 0.9144,
        "foot": 0.3048, "feet": 0.3048, "ft": 0.3048,
        "inch": 0.0254, "inches": 0.0254, "in": 0.0254,
    },
    "mass": {  # Base: kilogram
        "kg": 1.0, "kilogram": 1.0, "kilograms": 1.0,
        "g": 0.001, "gram": 0.001, "grams": 0.001,
        "mg": 0.000001, "milligram": 0.000001, "milligrams": 0.000001,
        "lb": 0.45359237, "lbs": 0.45359237, "pound": 0.45359237, "pounds": 0.45359237,
        "oz": 0.028349523125, "ounce": 0.028349523125, "ounces": 0.028349523125,
    },
    "volume": {  # Base: liter
        "l": 1.0, "liter": 1.0, "liters": 1.0,
        "ml": 0.001, "milliliter": 0.001, "milliliters": 0.001,
        "gal": 3.78541, "gallon": 3.78541, "gallons": 3.78541,
        "qt": 0.946353, "quart": 0.946353,
        "pt": 0.473176, "pint": 0.473176,
        "cup": 0.24, "cups": 0.24,
    },
    "time": {  # Base: second
        "sec": 1.0, "second": 1.0, "seconds": 1.0, "s": 1.0,
        "min": 60.0, "minute": 60.0, "minutes": 60.0,
        "hr": 3600.0, "hour": 3600.0, "hours": 3600.0, "h": 3600.0,
        "day": 86400.0, "days": 86400.0,
        "week": 604800.0, "weeks": 604800.0,
        "year": 31536000.0, "years": 31536000.0,
    }
}


def unit_convert(value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
    """Convert quantities between physical units."""
    from_u = from_unit.lower().strip()
    to_u = to_unit.lower().strip()
    
    # Handle temperature conversions separately
    temp_units = {"c", "celsius", "degc", "f", "fahrenheit", "degf", "k", "kelvin"}
    if from_u in temp_units and to_u in temp_units:
        # Convert from_u to Celsius first
        if from_u in ("c", "celsius", "degc"):
            c_val = value
        elif from_u in ("f", "fahrenheit", "degf"):
            c_val = (value - 32) * 5 / 9
        elif from_u in ("k", "kelvin"):
            c_val = value - 273.15
        else:
            return {"status": "error", "error": f"Invalid temperature unit: {from_unit}"}
            
        # Convert Celsius to to_u
        if to_u in ("c", "celsius", "degc"):
            final_val = c_val
        elif to_u in ("f", "fahrenheit", "degf"):
            final_val = (c_val * 9 / 5) + 32
        elif to_u in ("k", "kelvin"):
            final_val = c_val + 273.15
        else:
            return {"status": "error", "error": f"Invalid temperature unit: {to_unit}"}
            
        return {
            "value": value,
            "from_unit": from_unit,
            "to_unit": to_unit,
            "result": round(final_val, 6),
            "status": "success"
        }
        
    # Search in categories table
    for category, units in CONVERSION_TABLE.items():
        if from_u in units and to_u in units:
            base_val = value * units[from_u]
            final_val = base_val / units[to_u]
            return {
                "category": category,
                "value": value,
                "from_unit": from_unit,
                "to_unit": to_unit,
                "result": round(final_val, 6),
                "status": "success"
            }
            
    return {
        "status": "error",
        "error": f"Cannot convert from '{from_unit}' to '{to_unit}'. Units must belong to same physical category."
    }


def financial_calc(
    calc_type: str,
    principal: float = 0.0,
    rate: float = 0.0,
    time: float = 0.0,
    compounding_frequency: int = 1,
    amount: float = 0.0
) -> Dict[str, Any]:
    """Perform financial interest, loan EMI, and percentage calculations."""
    ctype = calc_type.lower().strip()
    try:
        if ctype in ("simple_interest", "simple"):
            interest = (principal * rate * time) / 100.0
            total_amount = principal + interest
            return {
                "calc_type": "simple_interest",
                "principal": principal,
                "rate": rate,
                "time_years": time,
                "interest": round(interest, 2),
                "total_amount": round(total_amount, 2),
                "status": "success"
            }
        elif ctype in ("compound_interest", "compound"):
            n = compounding_frequency
            total_amount = principal * math.pow(1 + (rate / (100.0 * n)), n * time)
            interest = total_amount - principal
            return {
                "calc_type": "compound_interest",
                "principal": principal,
                "rate": rate,
                "time_years": time,
                "compounding_per_year": n,
                "interest": round(interest, 2),
                "total_amount": round(total_amount, 2),
                "status": "success"
            }
        elif ctype in ("loan_emi", "emi"):
            # time is in years, convert to months
            months = int(time * 12) if time > 0 else int(amount) # fallback if months passed
            monthly_rate = rate / (12.0 * 100.0)
            if monthly_rate == 0:
                emi = principal / months
            else:
                emi = (principal * monthly_rate * math.pow(1 + monthly_rate, months)) / (math.pow(1 + monthly_rate, months) - 1)
            total_payment = emi * months
            total_interest = total_payment - principal
            return {
                "calc_type": "loan_emi",
                "principal": principal,
                "rate_annual": rate,
                "tenure_months": months,
                "monthly_emi": round(emi, 2),
                "total_interest": round(total_interest, 2),
                "total_payment": round(total_payment, 2),
                "status": "success"
            }
        elif ctype in ("percentage", "percent"):
            # Calculate percentage of a value or percentage change
            if amount > 0:
                perc_val = (principal * rate) / 100.0 if rate > 0 else (principal / amount) * 100.0
            else:
                perc_val = (principal * rate) / 100.0
            return {
                "calc_type": "percentage",
                "result": round(perc_val, 4),
                "status": "success"
            }
        else:
            return {"status": "error", "error": f"Unknown financial calculation type: {calc_type}"}
    except Exception as err:
        return {"status": "error", "error": str(err)}


def statistics_calc(operation: str, data: List[float]) -> Dict[str, Any]:
    """Calculate statistical metrics for a dataset."""
    if not data:
        return {"status": "error", "error": "Dataset cannot be empty"}
        
    op = operation.lower().strip()
    try:
        if op == "mean":
            res = statistics.mean(data)
        elif op == "median":
            res = statistics.median(data)
        elif op == "mode":
            res = statistics.mode(data)
        elif op in ("variance", "var"):
            res = statistics.variance(data) if len(data) > 1 else 0.0
        elif op in ("stdev", "std"):
            res = statistics.stdev(data) if len(data) > 1 else 0.0
        elif op in ("summary", "all"):
            return {
                "count": len(data),
                "sum": sum(data),
                "min": min(data),
                "max": max(data),
                "mean": round(statistics.mean(data), 4),
                "median": round(statistics.median(data), 4),
                "stdev": round(statistics.stdev(data), 4) if len(data) > 1 else 0.0,
                "status": "success"
            }
        else:
            return {"status": "error", "error": f"Unsupported statistical operation: {operation}"}
            
        return {
            "operation": operation,
            "data_count": len(data),
            "result": round(res, 6),
            "status": "success"
        }
    except Exception as err:
        return {"status": "error", "error": str(err)}
