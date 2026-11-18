// START_MODULE_CONTRACT
//   PURPOSE: Client-side share helpers for display (rules live in backend app/services/shares.py).
//   SCOPE: Sum of active shares for the stream footer.
//   DEPENDS: none
//   LINKS: M-FRONTEND-SHARED, V-M-FRONTEND-SHARED
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   TOTAL_SHARE    - 100
//   activeShareSum - sum of shares of active offers
// END_MODULE_MAP
export const TOTAL_SHARE = 100

export function activeShareSum(offers: { share: number; status: string }[]): number {
  return offers.filter((o) => o.status === 'active').reduce((acc, o) => acc + o.share, 0)
}
