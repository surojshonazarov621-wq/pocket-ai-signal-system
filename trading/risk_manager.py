
class RiskManager:
    def __init__(
        self,
        risk_percent=1.0,
        min_stake=1.0,
        max_stake=25.0,
        daily_loss_percent=5.0,
        max_consecutive_losses=4,
        max_daily_trades=1000,
        enabled=True,
        martingale_enabled=False,
        multiplier=2.2,
    ):
        if not 0 < risk_percent <= 100:
            raise ValueError("Risk foizi 0 dan 100 gacha bo'lishi kerak")
        if min_stake <= 0 or max_stake < min_stake:
            raise ValueError("Stavka chegaralari noto'g'ri")
        if not 0 < daily_loss_percent <= 100:
            raise ValueError("Kunlik zarar foizi noto'g'ri")
        if max_consecutive_losses < 1 or max_daily_trades < 1:
            raise ValueError("Savdo limitlari noto'g'ri")

        self.risk_percent = float(risk_percent)
        self.min_stake = float(min_stake)
        self.max_stake = float(max_stake)
        self.daily_loss_percent = float(daily_loss_percent)
        self.max_consecutive_losses = int(max_consecutive_losses)
        self.max_daily_trades = int(max_daily_trades)
        self.enabled = bool(enabled)
        self.martingale_enabled = bool(martingale_enabled)
        self.multiplier = float(multiplier)

    def update_settings(self, **settings):
        allowed = {
            "risk_percent", "min_stake", "max_stake",
            "daily_loss_percent", "max_consecutive_losses",
            "max_daily_trades", "enabled", "martingale_enabled"
        }

        for key, value in settings.items():
            if key not in allowed:
                raise ValueError(f"Noma'lum sozlama: {key}")
            setattr(self, key, value)

        if not 0 < self.risk_percent <= 100:
            raise ValueError("Risk foizi noto'g'ri")
        if self.min_stake <= 0 or self.max_stake < self.min_stake:
            raise ValueError("Stavka chegaralari noto'g'ri")

    def calculate_stake(
        self, balance, losses=0, daily_loss=0,
        daily_trades=0, day_start_balance=None
    ):
        if not self.enabled:
            return {"allowed": False, "reason": "Risk boshqaruvi o'chirilgan"}

        if balance <= 0:
            return {"allowed": False, "reason": "Balans yetarli emas"}

        if losses >= self.max_consecutive_losses:
            return {"allowed": False, "reason": "Ketma-ket zarar limiti tugadi"}

        if daily_trades >= self.max_daily_trades:
            return {"allowed": False, "reason": "Kunlik savdolar limiti tugadi"}

        start_balance = day_start_balance or balance
        daily_limit = start_balance * self.daily_loss_percent / 100

        if daily_loss >= daily_limit:
            return {"allowed": False, "reason": "Kunlik zarar limiti tugadi"}

        stake = round(balance * self.risk_percent / 100, 2)

        # Martingale stavkani oshirmaydi: risk foizi qat'iy chegara.
        if stake < self.min_stake:
            return {"allowed": False, "reason": "Hisoblangan stavka minimal stavkadan past"}

        stake = min(stake, self.max_stake)

        if daily_loss + stake > daily_limit:
            return {"allowed": False, "reason": "Kunlik zarar chegarasidan oshadi"}

        return {
            "allowed": True,
            "stake": round(stake, 2),
            "risk_percent": self.risk_percent,
            "daily_limit": round(daily_limit, 2),
            "daily_loss": round(daily_loss, 2),
            "remaining_daily_risk": round(daily_limit - daily_loss, 2),
        }

    def check_daily_limit(self, daily_loss, next_stake, balance=None):
        if balance is None or balance <= 0:
            return False

        limit = balance * self.daily_loss_percent / 100
        return daily_loss + next_stake <= limit
