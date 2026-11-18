// START_MODULE_CONTRACT
//   PURPOSE: Mutation saving manual offer shares / states for a stream.
//   SCOPE: PUT /api/campaigns/{cid}/streams/{sid}/offers + cache invalidation.
//   DEPENDS: M-FRONTEND-ENTITIES, M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-FEATURES, V-M-FRONTEND-FEATURES
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   useSetOffers - TanStack mutation
//   DraftOffer - editable (offer_id, share, state)
// END_MODULE_MAP
import { useMutation, useQueryClient } from '@tanstack/react-query'

import { campaignKeys } from '@/entities/campaign'
import { api, unwrap, type Schemas } from '@/shared/api'

export type DraftOffer = Schemas['OfferShareIn'] & { state: 'active' | 'disabled' }

export function useSetOffers(campaignId: number, streamId: number) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (offers: DraftOffer[]) =>
      unwrap(
        await api.PUT('/api/campaigns/{campaign_id}/streams/{stream_id}/offers', {
          params: { path: { campaign_id: campaignId, stream_id: streamId } },
          body: { offers },
        }),
      ),
    onSettled: () =>
      Promise.all([
        qc.invalidateQueries({ queryKey: campaignKeys.editorAll(campaignId) }),
        qc.invalidateQueries({ queryKey: campaignKeys.changes(campaignId) }),
      ]),
  })
}
