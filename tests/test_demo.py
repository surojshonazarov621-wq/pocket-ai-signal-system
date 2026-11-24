
import pytest
from trading.demo_trading import DemoTrading
from trading.risk_manager import RiskManager


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


def test_risk_manager_calculates_stake():
    risk = RiskManager(risk_percent=1)
    result = risk.calculate_stake(
        balance=100,
        day_start_balance=100
    )
    assert result["allowed"] is True
    assert result["stake"] == 1.0


def test_daily_loss_limit():
    risk = RiskManager(daily_loss_percent=5)
    result = risk.calculate_stake(
        balance=100,
        daily_loss=5,
        day_start_balance=100
    )
    assert result["allowed"] is False


def test_consecutive_loss_limit():
    risk = RiskManager(max_consecutive_losses=4)
    result = risk.calculate_stake(
        balance=100,
        losses=4,
        day_start_balance=100
    )
    assert result["allowed"] is False


def test_daily_trade_limit():
    risk = RiskManager(max_daily_trades=1000)
    result = risk.calculate_stake(
        balance=100,
        daily_trades=1000,
        day_start_balance=100
    )
    assert result["allowed"] is False


def test_risk_manager_can_be_disabled():
    risk = RiskManager(enabled=False)
    result = risk.calculate_stake(
        balance=100,
        day_start_balance=100
    )
    assert result["allowed"] is False
