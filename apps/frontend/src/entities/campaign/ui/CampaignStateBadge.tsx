// START_MODULE_CONTRACT
//   PURPOSE: Badge for Keitaro campaign / stream / offer state.
//   SCOPE: Presentational.
//   DEPENDS: M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-ENTITIES, V-M-FRONTEND-ENTITIES
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   StateBadge - active / disabled / other
// END_MODULE_MAP
import { Badge } from '@/shared/ui/badge'

const LABELS: Record<string, string> = { active: 'активна', disabled: 'выключена', deleted: 'удалена', removed: 'removed' }

export function StateBadge({ state }: { state: string }) {
  return <Badge variant={state === 'active' ? 'secondary' : 'outline'}>{LABELS[state] ?? state}</Badge>
}
