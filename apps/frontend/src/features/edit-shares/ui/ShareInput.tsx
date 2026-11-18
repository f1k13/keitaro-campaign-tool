// START_MODULE_CONTRACT
//   PURPOSE: Numeric 0..100 share input used in manual edit mode.
//   SCOPE: Presentational.
//   DEPENDS: M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-FEATURES, V-M-FRONTEND-FEATURES
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   ShareInput - clamps to integer 0..100
// END_MODULE_MAP
import { Input } from '@/shared/ui/input'

export function ShareInput({
  value,
  onChange,
  disabled,
}: {
  value: number
  onChange: (v: number) => void
  disabled?: boolean
}) {
  return (
    <div className="flex items-center justify-end gap-1">
      <Input
        type="number"
        min={0}
        max={100}
        step={1}
        value={value}
        disabled={disabled}
        onChange={(e) => {
          const n = Math.round(Number(e.target.value))
          onChange(Number.isFinite(n) ? Math.min(100, Math.max(0, n)) : 0)
        }}
        className="h-8 w-20 text-right tabular-nums"
      />
      <span className="text-muted-foreground">%</span>
    </div>
  )
}
