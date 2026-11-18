// START_MODULE_CONTRACT
//   PURPOSE: Push log of the selected campaign: Keitaro offers before -> after (from local PostgreSQL).
//   SCOPE: Read-only table.
//   DEPENDS: M-FRONTEND-ENTITIES, M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-WIDGETS, V-M-FRONTEND-WIDGETS
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   OfferChangesLog - before → after offers (names + shares) per push
// END_MODULE_MAP
import { useOfferChanges } from '@/entities/campaign'
import { Badge } from '@/shared/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/shared/ui/table'

const ACTIONS: Record<string, string> = { push: 'Push', add: 'добавлен', remove: 'удалён', update: 'доли изменены' }

type Snapshot = { offer_id?: number; share?: number; state?: string }

function OfferList({ list, names }: { list: Snapshot[]; names: Map<number, string> }) {
  if (list.length === 0) return <span>—</span>
  return (
    <ul className="grid gap-0.5">
      {list.map((o) => {
        const name = (o.offer_id !== undefined && names.get(o.offer_id)) || `Offer #${o.offer_id}`
        return (
          <li key={o.offer_id} className="flex gap-2" title={`ID ${o.offer_id}`}>
            <span className="w-10 shrink-0 text-right tabular-nums">{o.share}%</span>
            <span className="max-w-72 truncate">{name}</span>
          </li>
        )
      })}
    </ul>
  )
}

export function OfferChangesLog({
  campaignId,
  offerNames = new Map(),
}: {
  campaignId: number
  // offer id -> name, taken from the editor view (falls back to "Offer #id")
  offerNames?: Map<number, string>
}) {
  const changes = useOfferChanges(campaignId)
  if (!changes.data?.length) return null
  return (
    <Card>
      <CardHeader>
        <CardTitle>История публикаций</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Когда</TableHead>
              <TableHead>Поток</TableHead>
              <TableHead>Действие</TableHead>
              <TableHead>Было</TableHead>
              <TableHead>Стало</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {changes.data.map((c) => (
              <TableRow key={c.id}>
                <TableCell className="whitespace-nowrap">{new Date(c.created_at).toLocaleString('ru-RU')}</TableCell>
                <TableCell className="font-mono text-xs">{c.stream_id}</TableCell>
                <TableCell>
                  <Badge variant="outline">
                    {ACTIONS[c.action] ?? c.action}
                    {c.offer_id ? ` #${c.offer_id}` : ''}
                  </Badge>
                </TableCell>
                <TableCell className="align-top text-xs text-muted-foreground">
                  <OfferList list={c.before as Snapshot[]} names={offerNames} />
                </TableCell>
                <TableCell className="align-top text-xs">
                  <OfferList list={c.after as Snapshot[]} names={offerNames} />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}
