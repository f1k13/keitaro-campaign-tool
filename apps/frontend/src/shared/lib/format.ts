// START_MODULE_CONTRACT
//   PURPOSE: Number formatting helpers for stats tables.
//   SCOPE: Pure formatting, ru-RU locale.
//   DEPENDS: none
//   LINKS: M-FRONTEND-SHARED, V-M-FRONTEND-SHARED
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   formatInt     - integer, ru-RU
//   formatMoney   - USD, ru-RU
//   formatPercent - percent with 2 decimals
// END_MODULE_MAP
const int = new Intl.NumberFormat('ru-RU')
const money = new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'USD', maximumFractionDigits: 2 })
const pct = new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 2 })

export const formatInt = (v: number) => int.format(v)
export const formatMoney = (v: number) => money.format(v)
export const formatPercent = (v: number) => `${pct.format(v)}%`
