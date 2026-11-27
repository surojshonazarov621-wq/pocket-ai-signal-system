import math


class RiskManager:
    def __init__(
        self,
        risk_percent=1.0,
        min_stake=1.0,
        max_stake=25.0,
        daily_loss_percent=5.0,
        max_consecutive_losses=5,
        max_daily_trades=1000,
        enabled=True,
        martingale_enabled=True,
        multiplier=2.2,
        max_attempts=5,
        daily_loss_limit=10.0,
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
        self.max_attempts = int(max_attempts)
        self.daily_loss_limit = (
            None if daily_loss_limit is None
            else float(daily_loss_limit)
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
            raise ValueError("Zarar limiti kamida 1 bo'lishi kerak")
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
            "risk_percent", "min_stake", "max_stake",
            "daily_loss_percent", "max_consecutive_losses",
            "max_daily_trades", "enabled", "martingale_enabled",
            "multiplier", "max_attempts", "daily_loss_limit",
        }

        unknown = set(settings) - allowed
        if unknown:
            raise ValueError(f"Noma'lum sozlama: {', '.join(unknown)}")

        old = {key: getattr(self, key) for key in settings}

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
                        self, key,
                        None if value is None else float(value)
                    )
                else:
                    setattr(self, key, float(value))

            self._validate_settings()

        except (TypeError, ValueError):
            for key, value in old.items():
                setattr(self, key, value)
            raise

    def _daily_limit(self, start_balance):
        if self.daily_loss_limit is not None:
            return self.daily_loss_limit
        return start_balance * self.daily_loss_percent / 100

    def calculate_stake(
        self,
        balance,
        losses=0,
        daily_loss=0,
        daily_trades=0,
        day_start_balance=None,
    ):
        try:
            balance = float(balance)
            daily_loss = float(daily_loss)
            losses = int(losses)
            daily_trades = int(daily_trades)
            start_balance = (
                balance if day_start_balance is None
                else float(day_start_balance)
            )
        except (TypeError, ValueError):
            return {"allowed": False, "reason": "Hisob qiymatlari noto'g'ri"}

        numbers = (balance, daily_loss, start_balance)
        if not all(math.isfinite(x) for x in numbers):
            return {"allowed": False, "reason": "Hisob qiymatlari noto'g'ri"}

        if not self.enabled:
            return {"allowed": False, "reason": "Risk boshqaruvi o'chirilgan"}

        if balance <= 0 or start_balance <= 0:
            return {"allowed": False, "reason": "Balans yetarli emas"}

        if daily_loss < 0 or losses < 0 or daily_trades < 0:
            return {"allowed": False, "reason": "Hisob qiymatlari noto'g'ri"}

        if losses >= self.max_consecutive_losses:
            return {
                "allowed": False,
                "reason": "Ketma-ket zarar limiti tugadi",
            }

        if self.martingale_enabled and losses >= self.max_attempts:
            return {
                "allowed": False,
                "reason": "Martingale urinishlari limiti tugadi",
            }

        if daily_trades >= self.max_daily_trades:
            return {
                "allowed": False,
                "reason": "Kunlik savdolar limiti tugadi",
            }

        daily_limit = self._daily_limit(start_balance)
        remaining_risk = daily_limit - daily_loss

        if remaining_risk <= 0:
            return {
                "allowed": False,
                "reason": "Kunlik zarar limiti tugadi",
            }

        # Bazaviy stavka kun boshidagi balansdan hisoblanadi.
        base_stake = round(start_balance * self.risk_percent / 100, 2)

        # Har bir mag'lubiyatdan keyin stavka 2.2 baravar oshadi.
        if self.martingale_enabled:
            proposed_stake = base_stake * (self.multiplier ** losses)
        else:
            proposed_stake = base_stake

        proposed_stake = round(proposed_stake, 2)

        # Stavka balans, maksimal stavka va kunlik limitdan oshmaydi.
        safe_stake = min(
            proposed_stake,
            self.max_stake,
            balance,
            remaining_risk,
        )

        # Sentgacha pastga yaxlitlaymiz, limitdan oshmasligi uchun.
        stake = math.floor(safe_stake * 100 + 1e-9) / 100

        if stake < self.min_stake:
            return {
                "allowed": False,
                "reason": "Stavka minimal miqdordan past yoki limit tugagan",
            }

        return {
            "allowed": True,
            "stake": round(stake, 2),
            "base_stake": base_stake,
            "attempt": losses + 1,
            "multiplier": self.multiplier if self.martingale_enabled else 1,
            "daily_limit": round(daily_limit, 2),
            "daily_loss": round(daily_loss, 2),
            "remaining_daily_risk": round(daily_limit - daily_loss - stake, 2),
        }

    def check_daily_limit(
        self,
        daily_loss,
        next_stake,
        balance=None,
        day_start_balance=None,
    ):
        try:
            daily_loss = float(daily_loss)
            next_stake = float(next_stake)

            if balance is None:
                return False

            balance = float(balance)
            start_balance = (
                balance if day_start_balance is None
                else float(day_start_balance)
            )
        except (TypeError, ValueError):
            return False

        if not all(math.isfinite(x) for x in (
            daily_loss, next_stake, balance, start_balance
        )):
            return False

        if daily_loss < 0 or next_stake <= 0:
            return False
        if balance <= 0 or start_balance <= 0:
            return False

        limit = self._daily_limit(start_balance)
        return daily_loss + next_stake <= limit + 1e-9
