
from datetime import datetime, timedelta, timezone
from trading.risk_manager import RiskManager


UZ_TIME = timezone(timedelta(hours=5))


class DemoTrading:

    def __init__(self, initial_balance=100.00):

        if initial_balance <= 0:
            raise ValueError("Balans musbat bo'lishi kerak")

        self.balance = round(float(initial_balance), 2)
        self.initial_balance = self.balance

        self.base_stake = 1.00
        self.loss_streak = 0

        self.daily_loss = 0.00
        self.daily_trades = 0
        self.max_daily_loss = 10.00
        self.max_attempts = 5

        self.current_day = datetime.now(UZ_TIME).date()

        self.risk = RiskManager(
            min_stake=1.00,
            max_stake=25.00,
            multiplier=2.2,
            max_attempts=5,
            daily_loss_limit=10.00
        )

        self.active_trade = None
        self.history = []

    def refresh_day(self):

        today = datetime.now(UZ_TIME).date()

        if today != self.current_day:

            if self.active_trade is not None:
                return False

            self.current_day = today
            self.daily_loss = 0.00
            self.daily_trades = 0
            self.loss_streak = 0

        return True

    def open_trade(self, signal):

        if not self.refresh_day():
            return {"error": "Oldingi savdoni yoping"}

        if self.active_trade is not None:
            return {"error": "Savdo allaqachon ochilgan"}

        if signal not in ["BUY", "SELL"]:
            return {"error": "NO TRADE"}

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
            return {"error": "Kunlik zarar limiti tugadi"}

        if stake > self.balance:
            return {"error": "Balans yetarli emas"}

        self.active_trade = {
            "signal": signal,
            "stake": stake,
            "attempt": self.loss_streak + 1,
            "opened_at": datetime.now(UZ_TIME).isoformat()
        }

        return {
            "status": "DEMO TRADE OPEN",
            "signal": signal,
            "stake": stake,
            "attempt": self.loss_streak + 1,
            "balance": self.balance
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
            self.balance = round(self.balance + profit, 2)
            self.loss_streak = 0

        else:

            profit = -stake
            self.balance = round(self.balance - stake, 2)
            self.daily_loss = round(
                self.daily_loss + stake, 2
            )
            self.loss_streak += 1

        self.daily_trades += 1

        record = {
            **trade,
            "outcome": outcome,
            "payout": payout,
            "profit": round(profit, 2),
            "balance": self.balance,
            "closed_at": datetime.now(UZ_TIME).isoformat()
        }

        self.history.append(record)
        self.active_trade = None

        return record

    def get_statistics(self):

        wins = sum(
            1 for trade in self.history
            if trade["outcome"] == "WIN"
        )

        losses = sum(
            1 for trade in self.history
            if trade["outcome"] == "LOSS"
        )

        total = len(self.history)

        return {
            "initial_balance": self.initial_balance,
            "current_balance": self.balance,
            "daily_loss": self.daily_loss,
            "daily_trades": self.daily_trades,
            "wins": wins,
            "losses": losses,
            "win_rate": round(
                wins / total * 100, 2
            ) if total else 0,
            "loss_streak": self.loss_streak,
            "active_trade": self.active_trade is not None
        }
