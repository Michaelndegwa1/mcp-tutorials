"""Unit tests for Calculator MCP engine routines."""

import pytest
from calculator_mcp.engine import (
    evaluate_expression,
    basic_arithmetic,
    scientific_calc,
    unit_convert,
    financial_calc,
    statistics_calc,
)


def test_evaluate_expression():
    res = evaluate_expression("2 * (3 + 4)")
    assert res["status"] == "success"
    assert res["result"] == 14

    res2 = evaluate_expression("sqrt(144) + sin(pi / 2)")
    assert res2["status"] == "success"
    assert res2["result"] == 13

    res3 = evaluate_expression("5^2")
    assert res3["status"] == "success"
    assert res3["result"] == 25


def test_basic_arithmetic():
    assert basic_arithmetic("add", [10, 20, 30])["result"] == 60
    assert basic_arithmetic("subtract", [100, 30, 20])["result"] == 50
    assert basic_arithmetic("multiply", [2, 3, 4])["result"] == 24
    assert basic_arithmetic("divide", [100, 4])["result"] == 25
    assert basic_arithmetic("divide", [100, 0])["status"] == "error"


def test_scientific_calc():
    assert scientific_calc("power", 2, 8)["result"] == 256
    assert scientific_calc("sqrt", 81)["result"] == 9
    assert scientific_calc("factorial", 5)["result"] == 120
    assert scientific_calc("log", 1000, 10)["result"] == 3


def test_unit_convert():
    res_len = unit_convert(1, "km", "m")
    assert res_len["status"] == "success"
    assert res_len["result"] == 1000

    res_temp = unit_convert(0, "degC", "degF")
    assert res_temp["status"] == "success"
    assert res_temp["result"] == 32

    res_time = unit_convert(1, "hr", "min")
    assert res_time["status"] == "success"
    assert res_time["result"] == 60


def test_financial_calc():
    res_si = financial_calc("simple_interest", principal=1000, rate=5, time=2)
    assert res_si["status"] == "success"
    assert res_si["interest"] == 100.0
    assert res_si["total_amount"] == 1100.0

    res_emi = financial_calc("loan_emi", principal=100000, rate=10, time=1)
    assert res_emi["status"] == "success"
    assert res_emi["monthly_emi"] > 0


def test_statistics_calc():
    data = [10, 20, 30, 40, 50]
    assert statistics_calc("mean", data)["result"] == 30
    assert statistics_calc("median", data)["result"] == 30
    summary = statistics_calc("summary", data)
    assert summary["count"] == 5
    assert summary["min"] == 10
    assert summary["max"] == 50
