
from datetime import datetime, timezone
from trading.risk_manager import RiskManager


class DemoTrading:

    def __init__(self, initial_balance=100.00):

        self.balance = float(initial_balance)
        self.initial_balance = float(initial_balance)

        self.base_stake = 1.00
        self.loss_streak = 0
        self.daily_loss = 0.00
        self.daily_trades = 0

        self.max_daily_loss = 10.00
        self.max_attempts = 5

        self.risk = RiskManager(
            min_stake=1.00,
            max_stake=25.00,
            multiplier=2.2,
            max_attempts=5,
            daily_loss_limit=10.00
        )

        self.active_trade = None
        self.history = []

    def open_trade(self, signal):

        if self.active_trade is not None:
            return {"error": "Oldingi savdo hali yopilmagan"}

        if signal not in ["BUY", "SELL"]:
            return {"error": "Signal NO TRADE"}

        result = self.risk.calculate_stake(
            self.base_stake,
            self.loss_streak
        )

        if not result["allowed"]:
            return {"error": result["reason"]}

        stake = result["stake"]

        if not self.risk.check_daily_limit(
            self.daily_loss, stake
        ):
            return {"error": "Kunlik zarar limiti"}

        if stake > self.balance:
            return {"error": "Balans yetarli emas"}

        self.active_trade = {
            "signal": signal,
            "stake": stake,
            "attempt": self.loss_streak + 1,
            "opened_at": datetime.now(
                timezone.utc
            ).isoformat()
        }

        return {
            "status": "DEMO TRADE OPEN",
            "signal": signal,
            "stake": stake,
            "attempt": self.loss_streak + 1,
            "balance": round(self.balance, 2)
        }

    def close_trade(self, outcome, payout=0.80):

        if self.active_trade is None:
            return {"error": "Ochiq savdo mavjud emas"}

        if outcome not in ["WIN", "LOSS"]:
            return {"error": "Noto'g'ri natija"}

        if not 0 <= payout <= 1:
            return {"error": "Payout noto'g'ri"}

        trade = self.active_trade
        stake = trade["stake"]

        if outcome == "WIN":
            profit = round(stake * payout, 2)
            self.balance += profit
            self.loss_streak = 0
        else:
            profit = -stake
            self.balance -= stake
            self.daily_loss += stake
            self.loss_streak += 1

        self.daily_trades += 1

        record = {
            **trade,
            "outcome": outcome,
            "payout": payout,
            "profit": round(profit, 2),
            "balance": round(self.balance, 2),
            "closed_at": datetime.now(
                timezone.utc
            ).isoformat()
        }

        self.history.append(record)
        self.active_trade = None

        return record

    def get_statistics(self):

        wins = sum(
            1 for t in self.history
            if t["outcome"] == "WIN"
        )

        losses = sum(
            1 for t in self.history
            if t["outcome"] == "LOSS"
        )

        return {
            "initial_balance": self.initial_balance,
            "current_balance": round(self.balance, 2),
            "daily_loss": round(self.daily_loss, 2),
            "daily_trades": self.daily_trades,
            "wins": wins,
            "losses": losses,
            "win_rate": round(
                wins / len(self.history) * 100, 2
            ) if self.history else 0,
            "loss_streak": self.loss_streak
        }
