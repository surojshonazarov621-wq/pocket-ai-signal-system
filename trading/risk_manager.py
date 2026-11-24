
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
        max_attempts=5,
        daily_loss_limit=None,
    ):
        self.risk_percent = float(risk_percent)
        self.min_stake = float(min_stake)
        self.max_stake = float(max_stake)
        self.daily_loss_percent = float(daily_loss_percent)
        self.max_consecutive_losses = int(max_consecutive_losses)
        self.max_daily_trades = int(max_daily_trades)

        self.enabled = bool(enabled)
        self.martingale_enabled = bool(martingale_enabled)
        self.multiplier = float(multiplier)

        # Eski demo_trading.py bilan moslik
        self.max_attempts = int(max_attempts)
        self.daily_loss_limit = (
            float(daily_loss_limit)
            if daily_loss_limit is not None
            else None
        )

        self._validate_settings()

    def _validate_settings(self):
        if not 0 < self.risk_percent <= 100:
            raise ValueError("Risk foizi 0 dan 100 gacha bo'lishi kerak")

        if self.min_stake <= 0 or self.max_stake < self.min_stake:
            raise ValueError("Stavka chegaralari noto'g'ri")

        if not 0 < self.daily_loss_percent <= 100:
            raise ValueError("Kunlik zarar foizi noto'g'ri")

        if self.max_consecutive_losses < 1:
            raise ValueError("Ketma-ket zarar limiti kamida 1 bo'lishi kerak")

        if self.max_daily_trades < 1:
            raise ValueError("Kunlik savdo limiti kamida 1 bo'lishi kerak")

        if self.max_attempts < 1:
            raise ValueError("Urinishlar soni kamida 1 bo'lishi kerak")

        if self.multiplier < 1:
            raise ValueError("Multiplier 1 yoki undan katta bo'lishi kerak")

        if self.daily_loss_limit is not None and self.daily_loss_limit <= 0:
            raise ValueError("Kunlik zarar limiti musbat bo'lishi kerak")

    def update_settings(self, **settings):
        allowed = {
            "risk_percent",
            "min_stake",
            "max_stake",
            "daily_loss_percent",
            "max_consecutive_losses",
            "max_daily_trades",
            "enabled",
            "martingale_enabled",
            "multiplier",
            "max_attempts",
            "daily_loss_limit",
        }

        unknown = set(settings) - allowed
        if unknown:
            raise ValueError(f"Noma'lum sozlama: {', '.join(unknown)}")

        old_settings = {
            key: getattr(self, key)
            for key in settings
        }

        try:
            for key, value in settings.items():
                if key in ("enabled", "martingale_enabled"):
                    setattr(self, key, bool(value))
                elif key in (
                    "max_consecutive_losses",
                    "max_daily_trades",
                    "max_attempts",
                ):
                    setattr(self, key, int(value))
                elif key == "daily_loss_limit":
                    setattr(
                        self,
                        key,
                        None if value is None else float(value)
                    )
                else:
                    setattr(self, key, float(value))

            self._validate_settings()

        except (TypeError, ValueError):
            for key, value in old_settings.items():
                setattr(self, key, value)
            raise

    def calculate_stake(
        self,
        balance,
        losses=0,
        daily_loss=0,
        daily_trades=0,
        day_start_balance=None,
    ):
        balance = float(balance)
        daily_loss = float(daily_loss)
        losses = int(losses)
        daily_trades = int(daily_trades)

        if not self.enabled:
            return {
                "allowed": False,
                "reason": "Risk boshqaruvi o'chirilgan",
            }

        if balance <= 0:
            return {
                "allowed": False,
                "reason": "Balans yetarli emas",
            }

        if daily_loss < 0 or losses < 0 or daily_trades < 0:
            return {
                "allowed": False,
                "reason": "Hisob qiymatlari noto'g'ri",
            }

        if losses >= self.max_consecutive_losses:
            return {
                "allowed": False,
                "reason": "Ketma-ket zarar limiti tugadi",
            }

        if daily_trades >= self.max_daily_trades:
            return {
                "allowed": False,
                "reason": "Kunlik savdolar limiti tugadi",
            }

        start_balance = (
            balance
            if day_start_balance is None
            else float(day_start_balance)
        )

        if start_balance <= 0:
            return {
                "allowed": False,
                "reason": "Kun boshidagi balans noto'g'ri",
            }

        if self.daily_loss_limit is not None:
            daily_limit = self.daily_loss_limit
        else:
            daily_limit = (
                start_balance * self.daily_loss_percent / 100
            )

        remaining_risk = daily_limit - daily_loss

        if remaining_risk <= 0:
            return {
                "allowed": False,
                "reason": "Kunlik zarar limiti tugadi",
            }

        stake = round(
            balance * self.risk_percent / 100,
            2
        )

        stake = min(
            stake,
            self.max_stake,
            remaining_risk,
            balance,
        )

        if stake < self.min_stake:
            return {
                "allowed": False,
                "reason": "Hisoblangan stavka minimal stavkadan past",
            }

        return {
            "allowed": True,
            "stake": round(stake, 2),
            "risk_percent": self.risk_percent,
            "daily_limit": round(daily_limit, 2),
            "daily_loss": round(daily_loss, 2),
            "remaining_daily_risk": round(
                daily_limit - daily_loss - stake,
                2
            ),
        }

    def check_daily_limit(
        self,
        daily_loss,
        next_stake,
        balance=None,
        day_start_balance=None,
    ):
        if balance is None or balance <= 0:
            return False

        start_balance = (
            balance
            if day_start_balance is None
            else day_start_balance
        )

        if start_balance <= 0:
            return False

        if self.daily_loss_limit is not None:
            limit = self.daily_loss_limit
        else:
            limit = start_balance * self.daily_loss_percent / 100

        return (
            daily_loss >= 0
            and next_stake > 0
            and daily_loss + next_stake <= limit
        )
