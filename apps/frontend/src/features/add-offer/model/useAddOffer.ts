// START_MODULE_CONTRACT
//   PURPOSE: Mutation adding an offer to a stream (backend rebalances shares equally).
//   SCOPE: POST /api/campaigns/{cid}/streams/{sid}/offers + cache invalidation.
//   DEPENDS: M-FRONTEND-ENTITIES, M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-FEATURES, V-M-FRONTEND-FEATURES
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   useAddOffer - TanStack mutation
// END_MODULE_MAP
import { useMutation, useQueryClient } from '@tanstack/react-query'

import { campaignKeys } from '@/entities/campaign'
import { api, unwrap } from '@/shared/api'

export function useAddOffer(campaignId: number, streamId: number) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (offerId: number) =>
      unwrap(
        await api.POST('/api/campaigns/{campaign_id}/streams/{stream_id}/offers', {
          params: { path: { campaign_id: campaignId, stream_id: streamId } },
          body: { offer_id: offerId },
        }),
      ),
    onSettled: () =>
      Promise.all([
        qc.invalidateQueries({ queryKey: campaignKeys.editorAll(campaignId) }),
        qc.invalidateQueries({ queryKey: campaignKeys.changes(campaignId) }),
      ]),
  })
}
