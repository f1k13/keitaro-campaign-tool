// START_MODULE_CONTRACT
//   PURPOSE: Offer editor page: pick campaign + stats period, edit offers per stream, change log.
//   SCOPE: Page composition.
//   DEPENDS: M-FRONTEND-FEATURES, M-FRONTEND-WIDGETS, M-FRONTEND-ENTITIES, M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-PAGES, V-M-FRONTEND-PAGES
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   OfferEditorPage - campaignId comes from the URL (?campaign=)
// END_MODULE_MAP
import { RefreshCw } from 'lucide-react'
import { useState } from 'react'

import { IntervalSelect } from '@/features/select-interval'
import { CampaignPicker } from '@/features/select-campaign'
import { OfferChangesLog } from '@/widgets/offer-changes-log'
import { StreamOffersCard } from '@/widgets/stream-offers'
import { useEditorView, type StatsInterval } from '@/entities/campaign'
import { Alert, AlertDescription } from '@/shared/ui/alert'
import { Button } from '@/shared/ui/button'
import { Skeleton } from '@/shared/ui/skeleton'

export function OfferEditorPage({
  campaignId,
  onSelectCampaign,
}: {
  campaignId: number | null
  onSelectCampaign: (id: number) => void
}) {
  const [interval, setInterval] = useState<StatsInterval>('all_time')
  const view = useEditorView(campaignId, interval)
  const label = view.data ? `${view.data.campaign_id} · ${view.data.campaign_name}` : campaignId ? `#${campaignId}` : null

  return (
    <div className="grid gap-6">
      <div className="flex flex-wrap items-center gap-3">
        <CampaignPicker selectedLabel={label} onSelect={onSelectCampaign} />
        <IntervalSelect value={interval} onChange={setInterval} />
        {campaignId && (
          <Button variant="ghost" size="icon" aria-label="Обновить" onClick={() => view.refetch()} disabled={view.isFetching}>
            <RefreshCw className={view.isFetching ? 'animate-spin' : ''} />
          </Button>
        )}
      </div>

      {!campaignId && <p className="text-muted-foreground">Выберите кампанию, чтобы редактировать её офферы.</p>}

      {view.error && (
        <Alert variant="destructive">
          <AlertDescription>{view.error.message}</AlertDescription>
        </Alert>
      )}

      {campaignId && view.isLoading && (
        <div className="grid gap-4">
          <Skeleton className="h-32" />
          <Skeleton className="h-48" />
        </div>
      )}

      {view.data &&
        view.data.streams.map((s) => (
          <StreamOffersCard key={s.id} campaignId={view.data.campaign_id} stream={s} busy={view.isFetching} />
        ))}

      {view.data && view.data.streams.length === 0 && <p className="text-muted-foreground">В кампании нет потоков.</p>}

      {campaignId && <OfferChangesLog campaignId={campaignId} />}
    </div>
  )
}
