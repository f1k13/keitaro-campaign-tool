// START_MODULE_CONTRACT
//   PURPOSE: Push log of the selected campaign: Keitaro offers before -> after (from local PostgreSQL).
//   SCOPE: Read-only table.
//   DEPENDS: M-FRONTEND-ENTITIES, M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-WIDGETS, V-M-FRONTEND-WIDGETS
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   OfferChangesLog - before → after shares per change
// END_MODULE_MAP
import { useOfferChanges } from '@/entities/campaign'
import { Badge } from '@/shared/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/shared/ui/table'

const ACTIONS: Record<string, string> = { push: 'Push', add: 'добавлен', remove: 'удалён', update: 'доли изменены' }

type Snapshot = { offer_id?: number; share?: number; state?: string }

function render(list: Snapshot[]) {
  if (list.length === 0) return '—'
  return list.map((o) => `#${o.offer_id}: ${o.share}%`).join(', ')
}

export function OfferChangesLog({ campaignId }: { campaignId: number }) {
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
                <TableCell className="text-xs text-muted-foreground">{render(c.before as Snapshot[])}</TableCell>
                <TableCell className="text-xs">{render(c.after as Snapshot[])}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}
