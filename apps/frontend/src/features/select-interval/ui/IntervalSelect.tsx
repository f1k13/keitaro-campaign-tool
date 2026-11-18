// START_MODULE_CONTRACT
//   PURPOSE: Stats period selector for the editor.
//   SCOPE: Presentational select over StatsInterval values.
//   DEPENDS: M-FRONTEND-ENTITIES, M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-FEATURES, V-M-FRONTEND-FEATURES
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   IntervalSelect - controlled select
// END_MODULE_MAP
import type { StatsInterval } from '@/entities/campaign'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/shared/ui/select'

const OPTIONS: { value: StatsInterval; label: string }[] = [
  { value: 'today', label: 'Сегодня' },
  { value: 'yesterday', label: 'Вчера' },
  { value: '7_days_ago', label: '7 дней' },
  { value: '1_month_ago', label: '30 дней' },
  { value: 'all_time', label: 'Всё время' },
]

export function IntervalSelect({ value, onChange }: { value: StatsInterval; onChange: (v: StatsInterval) => void }) {
  return (
    <Select value={value} onValueChange={(v) => onChange(v as StatsInterval)}>
      <SelectTrigger className="w-40">
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        {OPTIONS.map((o) => (
          <SelectItem key={o.value} value={o.value}>
            {o.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}
