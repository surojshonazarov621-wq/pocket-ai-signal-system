
from datetime import datetime, timedelta, timezone
from trading.risk_manager import RiskManager

UZ_TIME = timezone(timedelta(hours=5))


class DemoTrading:
    def __init__(self, initial_balance=100.0):
        if initial_balance <= 0:
            raise ValueError("Balans musbat bo'lishi kerak")

        self.balance = round(float(initial_balance), 2)
        self.initial_balance = self.balance
        self.base_stake = 1.0
        self.loss_streak = 0
        self.daily_loss = 0.0
        self.daily_trades = 0
        self.max_daily_loss = 10.0
        self.max_attempts = 5
        self.current_day = datetime.now(UZ_TIME).date()

        self.risk = RiskManager(
            risk_percent=1.0,
            min_stake=1.0,
            max_stake=25.0,
            max_daily_trades=1000,
            max_consecutive_losses=5,
            martingale_enabled=False,
            multiplier=2.2,
            max_attempts=5,
            daily_loss_limit=self.max_daily_loss
        )

        self.active_trade = None
        self.history = []

    def refresh_day(self):
        today = datetime.now(UZ_TIME).date()

        if today != self.current_day:
            if self.active_trade:
                return False

            self.current_day = today
            self.daily_loss = 0.0
            self.daily_trades = 0
            self.loss_streak = 0

        return True

    def open_trade(self, signal):
        if not self.refresh_day():
            return {"error": "Oldingi savdoni yoping"}

        if self.active_trade:
            return {"error": "Savdo allaqachon ochilgan"}

        if signal not in ("BUY", "SELL"):
            return {"error": "NO TRADE"}

        result = self.risk.calculate_stake(
            balance=self.balance,
            losses=self.loss_streak,
            daily_loss=self.daily_loss,
            daily_trades=self.daily_trades,
            day_start_balance=self.initial_balance
        )

        if not result["allowed"]:
            return {"error": result["reason"]}

        stake = result["stake"]

        if not self.risk.check_daily_limit(
            daily_loss=self.daily_loss,
            next_stake=stake,
            balance=self.balance,
            day_start_balance=self.initial_balance
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
        if not self.active_trade:
            return {"error": "Ochiq savdo mavjud emas"}

        if outcome not in ("WIN", "LOSS"):
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
            self.daily_loss = round(self.daily_loss + stake, 2)
            self.loss_streak += 1

        self.daily_trades += 1

        record = {
            **trade,
            "outcome": outcome,
            "payout": payout,
            "profit": profit,
            "balance": self.balance,
            "closed_at": datetime.now(UZ_TIME).isoformat()
        }

        self.history.append(record)
        self.active_trade = None

        return record

    def get_statistics(self):
        wins = sum(t["outcome"] == "WIN" for t in self.history)
        losses = sum(t["outcome"] == "LOSS" for t in self.history)
        total = len(self.history)

        return {
            "initial_balance": self.initial_balance,
            "current_balance": self.balance,
            "daily_loss": self.daily_loss,
            "daily_trades": self.daily_trades,
            "wins": wins,
            "losses": losses,
            "win_rate": round(wins / total * 100, 2) if total else 0,
            "loss_streak": self.loss_streak,
            "active_trade": self.active_trade is not None
        }
