
class RiskManager:

    def __init__(
        self,
        min_stake=1.00,
        max_stake=10.00,
        multiplier=2.2,
        max_attempts=5,
        daily_loss_limit=20.00
    ):
        self.min_stake = min_stake
        self.max_stake = max_stake
        self.multiplier = multiplier
        self.max_attempts = max_attempts
        self.daily_loss_limit = daily_loss_limit

    def calculate_stake(self, base_stake, losses):
        if losses < 0 or losses >= self.max_attempts:
            return {
                "allowed": False,
                "reason": "Urinishlar limiti tugadi"
            }

        stake = round(
            base_stake * (self.multiplier ** losses), 2
        )

        if stake < self.min_stake:
            return {
                "allowed": False,
                "reason": "Minimal stavkadan past"
            }

        if stake > self.max_stake:
            return {
                "allowed": False,
                "reason": "Maksimal stavka limiti oshdi"
            }

        return {
            "allowed": True,
            "stake": stake,
            "attempt": losses + 1,
            "multiplier": self.multiplier
        }

    def check_daily_limit(self, daily_loss, next_stake):
        if daily_loss + next_stake > self.daily_loss_limit:
            return False

        return True
