// START_MODULE_CONTRACT
//   PURPOSE: Stream header info: position, type, schema, filters, redirect target.
//   SCOPE: Presentational.
//   DEPENDS: M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-ENTITIES, V-M-FRONTEND-ENTITIES
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   StreamMeta - badges + filter/redirect description
// END_MODULE_MAP
import type { Schemas } from '@/shared/api'
import { Badge } from '@/shared/ui/badge'

const TYPE_LABELS: Record<string, string> = {
  forced: 'перехват',
  regular: 'обычный',
  default: 'по умолчанию',
}

const SCHEMA_LABELS: Record<string, string> = {
  redirect: 'редирект',
  landings: 'лендинги и офферы',
  action: 'действие',
}

export function StreamMeta({ stream }: { stream: Schemas['StreamView'] }) {
  return (
    <div className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
      <Badge variant="outline">#{stream.position}</Badge>
      <Badge variant="secondary">{TYPE_LABELS[stream.type] ?? stream.type}</Badge>
      {stream.stream_schema && <Badge variant="outline">{SCHEMA_LABELS[stream.stream_schema] ?? stream.stream_schema}</Badge>}
      {stream.filters.length > 0 && <span>фильтры: {stream.filters.join('; ')}</span>}
      {stream.stream_schema === 'redirect' && stream.action_payload && <span>→ {stream.action_payload}</span>}
    </div>
  )
}
