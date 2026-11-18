# START_MODULE_CONTRACT
#   PURPOSE: Pure share arithmetic for offers inside one Keitaro stream (pinned-aware).
#   SCOPE: Equal split with deterministic remainder, rebalance around pinned weights, publish validation.
#   DEPENDS: none
#   LINKS: M-OFFER-EDITOR, V-M-OFFER-EDITOR
# END_MODULE_CONTRACT
#
# START_MODULE_MAP
#   TOTAL               - 100
#   ShareSlot           - (offer_id, share, active, pinned) value object
#   split_equally       - split an integer total into n parts differing by at most 1
#   rebalance           - pinned keep share, rest of 100 split equally among unpinned active, removed get 0
#   validate_publishable - raises ValidationFailedError unless >=1 active offer and active shares sum to 100
# END_MODULE_MAP
from dataclasses import dataclass, replace

from app.core.errors import ValidationFailedError

TOTAL = 100


@dataclass(frozen=True)
class ShareSlot:
    offer_id: int
    share: int
    active: bool
    pinned: bool = False


# START_CONTRACT: split_equally
#   PURPOSE: Split `total` into n integer parts that differ by at most 1.
#   INPUTS: { n: int - number of parts, total: int - amount to split (default 100) }
#   OUTPUTS: { list[int] - first (total % n) parts get +1; sum == total when n > 0 }
#   SIDE_EFFECTS: none
# END_CONTRACT: split_equally
def split_equally(n: int, total: int = TOTAL) -> list[int]:
    if n <= 0:
        return []
    base, remainder = divmod(total, n)
    return [base + 1 if i < remainder else base for i in range(n)]


# START_CONTRACT: rebalance
#   PURPOSE: Recompute shares after any draft action (add / remove / bring back / pin / unpin).
#   INPUTS: { slots: list[ShareSlot] - in display order }
#   OUTPUTS: { list[ShareSlot] - pinned active keep share; 100 - pinned sum split equally (list order)
#              among unpinned active; removed offers 0 and unpinned }
#   SIDE_EFFECTS: raises ValidationFailedError when pinned active shares exceed 100
# END_CONTRACT: rebalance
def rebalance(slots: list[ShareSlot]) -> list[ShareSlot]:
    pinned_sum = sum(s.share for s in slots if s.active and s.pinned)
    if pinned_sum > TOTAL:
        raise ValidationFailedError(f"Сумма запиненных долей {pinned_sum}% больше 100%")
    free = [s for s in slots if s.active and not s.pinned]
    parts = iter(split_equally(len(free), TOTAL - pinned_sum))
    result: list[ShareSlot] = []
    for s in slots:
        if not s.active:
            result.append(replace(s, share=0, pinned=False))
        elif s.pinned:
            result.append(s)
        else:
            result.append(replace(s, share=next(parts)))
    return result


# START_CONTRACT: validate_publishable
#   PURPOSE: Guard Push: Keitaro must receive at least one active offer and shares summing to exactly 100.
#   INPUTS: { slots: list[ShareSlot] }
#   OUTPUTS: { None }
#   SIDE_EFFECTS: raises ValidationFailedError when no offer is active or the active sum != 100
# END_CONTRACT: validate_publishable
def validate_publishable(slots: list[ShareSlot]) -> None:
    active = [s for s in slots if s.active]
    if not active:
        raise ValidationFailedError(
            "Нет активных офферов: трафику потока некуда идти, верните или добавьте оффер"
        )
    total = sum(s.share for s in active)
    if total != TOTAL:
        raise ValidationFailedError(
            f"Сумма долей активных офферов {total}% вместо 100%: открепите пин или поменяйте его значение"
        )
