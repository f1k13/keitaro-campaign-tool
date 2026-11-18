// START_MODULE_CONTRACT
//   PURPOSE: Campaign creator page: form, last result, history of created campaigns.
//   SCOPE: Page composition.
//   DEPENDS: M-FRONTEND-FEATURES, M-FRONTEND-WIDGETS, M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-PAGES, V-M-FRONTEND-PAGES
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   CreateCampaignPage - onOpenEditor(campaignId) switches to the editor
// END_MODULE_MAP
import { CheckCircle2 } from 'lucide-react'
import { useState } from 'react'

import { CreateCampaignForm } from '@/features/create-campaign'
import { CreatedCampaignsTable } from '@/widgets/created-campaigns'
import type { Schemas } from '@/shared/api'
import { Alert, AlertDescription, AlertTitle } from '@/shared/ui/alert'
import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card'

export function CreateCampaignPage({ onOpenEditor }: { onOpenEditor: (campaignId: number) => void }) {
  const [last, setLast] = useState<Schemas['CampaignCreated'] | null>(null)
  return (
    <div className="grid gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Новая кампания</CardTitle>
          <CardDescription>
            Создаст кампанию с двумя потоками: трафик из выбранной страны → Google, остальной трафик → оффер.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <CreateCampaignForm onCreated={setLast} />
        </CardContent>
      </Card>

      {last && (
        <Alert>
          <CheckCircle2 />
          <AlertTitle>
            Кампания «{last.name}» создана (ID {last.campaign_id})
          </AlertTitle>
          <AlertDescription>
            <div className="grid gap-1">
              {last.url && (
                <a href={last.url} target="_blank" rel="noreferrer" className="underline underline-offset-4">
                  {last.url}
                </a>
              )}
              <span>
                Поток #{last.geo_stream_id}: {last.country} → Google · Поток #{last.offer_stream_id}: оффер #{last.offer_id} (100%)
              </span>
              <div className="pt-2">
                <Button size="sm" variant="outline" onClick={() => onOpenEditor(last.campaign_id)}>
                  Открыть в редакторе
                </Button>
              </div>
            </div>
          </AlertDescription>
        </Alert>
      )}

      <CreatedCampaignsTable onEdit={onOpenEditor} />
    </div>
  )
}
