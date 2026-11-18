// START_MODULE_CONTRACT
//   PURPOSE: One campaign stream with its offers: shares, stats, add/remove, manual share editing.
//   SCOPE: Composes add-offer, remove-offer, edit-shares features with offer/stream entities.
//   DEPENDS: M-FRONTEND-FEATURES, M-FRONTEND-ENTITIES, M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-WIDGETS, V-M-FRONTEND-WIDGETS
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   StreamOffersCard - card per stream; offer table only for "landings" streams
// END_MODULE_MAP
import { Loader2, Pencil, Scale } from 'lucide-react'
import { useState } from 'react'
import { toast } from 'sonner'

import { AddOfferButton } from '@/features/add-offer'
import { ShareInput, useSetOffers, type DraftOffer } from '@/features/edit-shares'
import { RemoveOfferButton } from '@/features/remove-offer'
import { StateBadge } from '@/entities/campaign'
import { OfferStatsCells, STATS_COLUMNS } from '@/entities/offer'
import { StreamMeta } from '@/entities/stream'
import type { Schemas } from '@/shared/api'
import { activeShareSum, splitEqually, TOTAL_SHARE } from '@/shared/lib/shares'
import { cn } from '@/shared/lib/utils'
import { Button } from '@/shared/ui/button'
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Table, TableBody, TableCell, TableFooter, TableHead, TableHeader, TableRow } from '@/shared/ui/table'

type Stream = Schemas['StreamView']

function toDraft(stream: Stream): DraftOffer[] {
  return stream.offers.map((o) => ({ offer_id: o.offer_id, share: o.share, state: o.state }))
}

export function StreamOffersCard({ campaignId, stream, busy }: { campaignId: number; stream: Stream; busy?: boolean }) {
  const [draft, setDraft] = useState<DraftOffer[] | null>(null)
  const save = useSetOffers(campaignId, stream.id)
  const editing = draft !== null
  const rows = editing ? draft : toDraft(stream)
  const sum = activeShareSum(rows)
  const hasActive = rows.some((o) => o.state === 'active')
  const sumOk = !hasActive || sum === TOTAL_SHARE

  const patch = (offerId: number, change: Partial<DraftOffer>) =>
    setDraft((d) => d && d.map((o) => (o.offer_id === offerId ? { ...o, ...change } : o)))

  const equalize = () =>
    setDraft((d) => {
      if (!d) return d
      const parts = splitEqually(d.filter((o) => o.state === 'active').length)
      let i = 0
      return d.map((o) => ({ ...o, share: o.state === 'active' ? parts[i++] : 0 }))
    })

  const submit = () =>
    draft &&
    save.mutate(draft, {
      onSuccess: () => {
        setDraft(null)
        toast.success('Доли сохранены в Keitaro')
      },
      onError: (e) => toast.error(e.message),
    })

  return (
    <Card className={cn(busy && 'opacity-70 transition-opacity')}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {stream.name || `Поток #${stream.id}`}
          <StateBadge state={stream.state} />
        </CardTitle>
        <CardDescription>
          <StreamMeta stream={stream} />
        </CardDescription>
        {stream.accepts_offers && (
          <CardAction className="flex gap-2">
            {editing ? (
              <>
                <Button size="sm" variant="outline" onClick={equalize}>
                  <Scale /> Поровну
                </Button>
                <Button size="sm" variant="ghost" onClick={() => setDraft(null)}>
                  Отмена
                </Button>
                <Button size="sm" onClick={submit} disabled={!sumOk || save.isPending}>
                  {save.isPending && <Loader2 className="animate-spin" />}
                  Сохранить
                </Button>
              </>
            ) : (
              <>
                <Button size="sm" variant="outline" disabled={stream.offers.length === 0} onClick={() => setDraft(toDraft(stream))}>
                  <Pencil /> Доли
                </Button>
                <AddOfferButton campaignId={campaignId} streamId={stream.id} existing={stream.offers.map((o) => o.offer_id)} />
              </>
            )}
          </CardAction>
        )}
      </CardHeader>

      {stream.accepts_offers && (
        <CardContent>
          {stream.offers.length === 0 ? (
            <p className="py-6 text-center text-sm text-muted-foreground">В потоке нет офферов — добавьте первый.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Оффер</TableHead>
                  <TableHead>Статус</TableHead>
                  <TableHead className="text-right">Доля</TableHead>
                  {STATS_COLUMNS.map((c) => (
                    <TableHead key={c} className="text-right">
                      {c}
                    </TableHead>
                  ))}
                  <TableHead className="w-10" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {stream.offers.map((offer) => {
                  const row = rows.find((r) => r.offer_id === offer.offer_id) ?? offer
                  return (
                    <TableRow key={offer.offer_id} className={cn(row.state !== 'active' && 'text-muted-foreground')}>
                      <TableCell className="max-w-80">
                        <div className="truncate font-medium">{offer.name}</div>
                        <div className="font-mono text-xs text-muted-foreground">#{offer.offer_id}</div>
                      </TableCell>
                      <TableCell>
                        {editing ? (
                          <Button
                            size="sm"
                            variant="outline"
                            className="h-7"
                            onClick={() => patch(offer.offer_id, { state: row.state === 'active' ? 'disabled' : 'active' })}
                          >
                            {row.state === 'active' ? 'Выключить' : 'Включить'}
                          </Button>
                        ) : (
                          <StateBadge state={row.state} />
                        )}
                      </TableCell>
                      <TableCell className="text-right tabular-nums">
                        {editing ? (
                          <ShareInput
                            value={row.share}
                            disabled={row.state !== 'active'}
                            onChange={(share) => patch(offer.offer_id, { share })}
                          />
                        ) : (
                          `${row.share}%`
                        )}
                      </TableCell>
                      <OfferStatsCells stats={offer.stats} />
                      <TableCell>
                        <RemoveOfferButton
                          campaignId={campaignId}
                          streamId={stream.id}
                          offerId={offer.offer_id}
                          offerName={offer.name}
                          disabled={editing}
                        />
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
              <TableFooter>
                <TableRow>
                  <TableCell colSpan={2}>Итого по потоку</TableCell>
                  <TableCell className={cn('text-right tabular-nums', !sumOk && 'text-destructive')}>{sum}%</TableCell>
                  <OfferStatsCells stats={stream.totals} />
                  <TableCell />
                </TableRow>
              </TableFooter>
            </Table>
          )}
          {editing && !sumOk && (
            <p className="mt-3 text-sm text-destructive">
              Сумма долей активных офферов должна быть 100% (сейчас {sum}%). Нажмите «Поровну» или поправьте вручную.
            </p>
          )}
        </CardContent>
      )}
    </Card>
  )
}
