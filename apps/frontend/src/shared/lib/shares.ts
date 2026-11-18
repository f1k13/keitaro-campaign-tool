// START_MODULE_CONTRACT
//   PURPOSE: Client-side preview of share arithmetic (mirrors backend app/services/shares.py).
//   SCOPE: Sum of active shares for manual editing validation.
//   DEPENDS: none
//   LINKS: M-FRONTEND-SHARED, V-M-FRONTEND-SHARED
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   TOTAL_SHARE - 100
//   activeShareSum - sum of shares of active offers
//   splitEqually - same algorithm as backend split_equally
// END_MODULE_MAP
export const TOTAL_SHARE = 100

export function activeShareSum(offers: { share: number; state: string }[]): number {
  return offers.filter((o) => o.state === 'active').reduce((acc, o) => acc + o.share, 0)
}

export function splitEqually(n: number): number[] {
  if (n <= 0) return []
  const base = Math.floor(TOTAL_SHARE / n)
  const remainder = TOTAL_SHARE - base * n
  return Array.from({ length: n }, (_, i) => (i < remainder ? base + 1 : base))
}
