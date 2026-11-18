// START_MODULE_CONTRACT
//   PURPOSE: One campaign stream: offers with shares, pins and stats; draft state (yellow) with Push/Cancel.
//   SCOPE: Composes add-offer, remove-offer, restore-offer, pin-offer, publish-stream features.
//   DEPENDS: M-FRONTEND-FEATURES, M-FRONTEND-ENTITIES, M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-WIDGETS, V-M-FRONTEND-WIDGETS
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   StreamOffersCard - card per stream; offer table only for "landings" streams
// END_MODULE_MAP
import { Pin } from 'lucide-react'

import { AddOfferButton } from '@/features/add-offer'
import { PinOfferControl } from '@/features/pin-offer'
import { PublishStreamActions } from '@/features/publish-stream'
import { RemoveOfferButton } from '@/features/remove-offer'
import { RestoreOfferButton } from '@/features/restore-offer'
import { StateBadge } from '@/entities/campaign'
import { OfferStatsCells, STATS_COLUMNS } from '@/entities/offer'
import { StreamMeta } from '@/entities/stream'
import type { Schemas } from '@/shared/api'
import { activeShareSum, TOTAL_SHARE } from '@/shared/lib/shares'
import { cn } from '@/shared/lib/utils'
import { Badge } from '@/shared/ui/badge'
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'
import { Table, TableBody, TableCell, TableFooter, TableHead, TableHeader, TableRow } from '@/shared/ui/table'

type Stream = Schemas['StreamView']

export function StreamOffersCard({ campaignId, stream, busy }: { campaignId: number; stream: Stream; busy?: boolean }) {
  const sum = activeShareSum(stream.offers)
  const hasActive = stream.offers.some((o) => o.status === 'active')
  // Same rule as backend validate_publishable: >=1 active offer and active shares sum to 100
  const publishable = hasActive && sum === TOTAL_SHARE
  const warning =
    stream.offers.length === 0 || publishable
      ? null
      : hasActive
        ? `Сумма долей активных офферов ${sum}% вместо 100% — открепите пин или поменяйте его значение, иначе Push не пройдёт.`
        : 'Нет активных офферов — трафику потока некуда идти. Верните или добавьте оффер, иначе Push не пройдёт.'
  const activeIds = stream.offers.filter((o) => o.status === 'active').map((o) => o.offer_id)

  return (
    <Card
      className={cn(
        busy && 'opacity-70 transition-opacity',
        stream.is_dirty && 'border-amber-300 bg-amber-50 dark:border-amber-700 dark:bg-amber-950/30',
      )}
    >
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {stream.name || `Поток #${stream.id}`}
          <StateBadge state={stream.state} />
          {stream.is_dirty && (
            <Badge className="bg-amber-400 text-amber-950 hover:bg-amber-400">Не опубликован</Badge>
          )}
        </CardTitle>
        <CardDescription>
          <StreamMeta stream={stream} />
        </CardDescription>
        {stream.accepts_offers && (
          <CardAction className="flex gap-2">
            {stream.is_dirty && <PublishStreamActions campaignId={campaignId} streamId={stream.id} disabled={busy} />}
            <AddOfferButton campaignId={campaignId} streamId={stream.id} existing={activeIds} disabled={busy} />
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
                  <TableHead className="text-right">Доля</TableHead>
                  {STATS_COLUMNS.map((c) => (
                    <TableHead key={c} className="text-right">
                      {c}
                    </TableHead>
                  ))}
                  <TableHead className="w-28" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {stream.offers.map((offer) => {
                  const removed = offer.status === 'removed'
                  return (
                    <TableRow key={offer.offer_id} className={cn(removed && 'text-muted-foreground opacity-60')}>
                      <TableCell className="max-w-80">
                        <div className="flex items-center gap-2">
                          <span className={cn('truncate font-medium', removed && 'line-through')}>{offer.name}</span>
                          {offer.is_new && <Badge variant="outline">новый</Badge>}
                          {removed && <Badge variant="outline">removed</Badge>}
                        </div>
                        <div className="font-mono text-xs text-muted-foreground">#{offer.offer_id}</div>
                      </TableCell>
                      <TableCell className="text-right tabular-nums">
                        <span className="inline-flex items-center gap-1">
                          {offer.pinned && <Pin className="size-3.5 text-primary" aria-label="запинен" />}
                          {offer.share}%
                        </span>
                      </TableCell>
                      <OfferStatsCells stats={offer.stats} />
                      <TableCell>
                        <div className="flex justify-end gap-1">
                          {removed ? (
                            <RestoreOfferButton
                              campaignId={campaignId}
                              streamId={stream.id}
                              offerId={offer.offer_id}
                              disabled={busy}
                            />
                          ) : (
                            <>
                              <PinOfferControl
                                campaignId={campaignId}
                                streamId={stream.id}
                                offerId={offer.offer_id}
                                share={offer.share}
                                pinned={offer.pinned}
                                disabled={busy}
                              />
                              <RemoveOfferButton
                                campaignId={campaignId}
                                streamId={stream.id}
                                offerId={offer.offer_id}
                                disabled={busy}
                              />
                            </>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
              <TableFooter>
                <TableRow>
                  <TableCell>Итого по потоку</TableCell>
                  <TableCell className={cn('text-right tabular-nums', warning && 'text-destructive')}>{sum}%</TableCell>
                  <OfferStatsCells stats={stream.totals} />
                  <TableCell />
                </TableRow>
              </TableFooter>
            </Table>
          )}
          {warning && <p className="mt-3 text-sm text-destructive">{warning}</p>}
        </CardContent>
      )}
    </Card>
  )
}
