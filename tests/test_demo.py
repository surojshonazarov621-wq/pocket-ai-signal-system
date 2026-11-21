import pytest
from trading.demo_trading import DemoTrading


def test_initial_balance():
    demo = DemoTrading(100)
    assert demo.balance == 100


def test_open_trade():
    demo = DemoTrading(100)
    result = demo.open_trade("BUY")
    assert result["status"] == "DEMO TRADE OPEN"


def test_invalid_signal():
    demo = DemoTrading(100)
    result = demo.open_trade("WAIT")
    assert "error" in result


def test_close_without_trade():
    demo = DemoTrading(100)
    result = demo.close_trade("WIN")
    assert "error" in result
