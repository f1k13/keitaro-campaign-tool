// START_MODULE_CONTRACT
//   PURPOSE: Mutation removing an offer from a stream (backend rebalances remaining shares).
//   SCOPE: DELETE /api/campaigns/{cid}/streams/{sid}/offers/{oid} + cache invalidation.
//   DEPENDS: M-FRONTEND-ENTITIES, M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-FEATURES, V-M-FRONTEND-FEATURES
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   useRemoveOffer - TanStack mutation
// END_MODULE_MAP
import { useMutation, useQueryClient } from '@tanstack/react-query'

import { campaignKeys } from '@/entities/campaign'
import { api, unwrap } from '@/shared/api'

export function useRemoveOffer(campaignId: number, streamId: number) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (offerId: number) =>
      unwrap(
        await api.DELETE('/api/campaigns/{campaign_id}/streams/{stream_id}/offers/{offer_id}', {
          params: { path: { campaign_id: campaignId, stream_id: streamId, offer_id: offerId } },
        }),
      ),
    onSettled: () =>
      Promise.all([
        qc.invalidateQueries({ queryKey: campaignKeys.editorAll(campaignId) }),
        qc.invalidateQueries({ queryKey: campaignKeys.changes(campaignId) }),
      ]),
  })
}
