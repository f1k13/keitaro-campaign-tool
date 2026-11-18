# START_MODULE_CONTRACT
#   PURPOSE: Pure share arithmetic for offers inside one Keitaro stream.
#   SCOPE: Equal split with deterministic remainder, validation of manual shares.
#   DEPENDS: none
#   LINKS: M-OFFER-EDITOR, V-M-OFFER-EDITOR
# END_MODULE_CONTRACT
#
# START_MODULE_MAP
#   TOTAL           - 100
#   OfferShare      - (offer_id, share, state) value object
#   split_equally   - integer shares summing to exactly 100
#   rebalance       - equal split over active offers, disabled get 0
#   validate_shares - raises ValidationFailedError on bad manual shares
# END_MODULE_MAP
from dataclasses import dataclass

from app.core.errors import ValidationFailedError

TOTAL = 100


@dataclass(frozen=True)
class OfferShare:
    offer_id: int
    share: int
    state: str = "active"

    def as_dict(self) -> dict[str, int | str]:
        return {"offer_id": self.offer_id, "share": self.share, "state": self.state}


# START_CONTRACT: split_equally
#   PURPOSE: Split 100% into n integer parts that differ by at most 1.
#   INPUTS: { n: int - number of parts, n >= 0 }
#   OUTPUTS: { list[int] - first (100 % n) parts get +1; sum == 100 when n > 0 }
#   SIDE_EFFECTS: none
# END_CONTRACT: split_equally
def split_equally(n: int) -> list[int]:
    if n <= 0:
        return []
    base, remainder = divmod(TOTAL, n)
    return [base + 1 if i < remainder else base for i in range(n)]


# START_CONTRACT: rebalance
#   PURPOSE: Recompute shares after add/remove: active offers split 100% equally in list order.
#   INPUTS: { offers: list[OfferShare] }
#   OUTPUTS: { list[OfferShare] - same order, disabled offers share 0 }
#   SIDE_EFFECTS: none
# END_CONTRACT: rebalance
def rebalance(offers: list[OfferShare]) -> list[OfferShare]:
    parts = iter(split_equally(sum(1 for o in offers if o.state == "active")))
    return [OfferShare(o.offer_id, next(parts) if o.state == "active" else 0, o.state) for o in offers]


# START_CONTRACT: validate_shares
#   PURPOSE: Reject manual share sets Keitaro would distribute incorrectly.
#   INPUTS: { offers: list[OfferShare] }
#   OUTPUTS: { None }
#   SIDE_EFFECTS: raises ValidationFailedError (duplicates, range, active sum != 100)
# END_CONTRACT: validate_shares
def validate_shares(offers: list[OfferShare]) -> None:
    ids = [o.offer_id for o in offers]
    if len(ids) != len(set(ids)):
        raise ValidationFailedError("Оффер добавлен в поток дважды")
    for o in offers:
        if not 0 <= o.share <= TOTAL:
            raise ValidationFailedError(f"Доля оффера {o.offer_id} должна быть от 0 до 100")
    active = [o for o in offers if o.state == "active"]
    total = sum(o.share for o in active)
    if active and total != TOTAL:
        raise ValidationFailedError(f"Сумма долей активных офферов должна быть 100%, сейчас {total}%")
