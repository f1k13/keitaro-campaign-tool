// START_MODULE_CONTRACT
//   PURPOSE: Table cells rendering offer stats (clicks, conversions, CR, revenue, EPC, profit).
//   SCOPE: Presentational, used in stream offer tables.
//   DEPENDS: M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-ENTITIES, V-M-FRONTEND-ENTITIES
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   STATS_COLUMNS - header labels
//   OfferStatsCells - <td> cells for one OfferStats
// END_MODULE_MAP
import type { Schemas } from '@/shared/api'
import { formatInt, formatMoney, formatPercent } from '@/shared/lib/format'
import { cn } from '@/shared/lib/utils'
import { TableCell } from '@/shared/ui/table'

export const STATS_COLUMNS = ['Клики', 'Конв.', 'CR', 'Доход', 'EPC', 'Прибыль'] as const

export function OfferStatsCells({ stats, className }: { stats: Schemas['OfferStats']; className?: string }) {
  const cell = cn('text-right tabular-nums', className)
  return (
    <>
      <TableCell className={cell}>{formatInt(stats.clicks)}</TableCell>
      <TableCell className={cell}>{formatInt(stats.conversions)}</TableCell>
      <TableCell className={cell}>{formatPercent(stats.cr)}</TableCell>
      <TableCell className={cell}>{formatMoney(stats.revenue)}</TableCell>
      <TableCell className={cell}>{formatMoney(stats.epc)}</TableCell>
      <TableCell className={cn(cell, stats.profit < 0 && 'text-destructive')}>{formatMoney(stats.profit)}</TableCell>
    </>
  )
}
