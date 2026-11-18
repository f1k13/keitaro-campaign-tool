// START_MODULE_CONTRACT
//   PURPOSE: Draft mutation removing an offer (greyed out, share 0, can be brought back).
//   SCOPE: DELETE /api/campaigns/{cid}/streams/{sid}/offers/{oid} + cache invalidation.
//   DEPENDS: M-FRONTEND-ENTITIES, M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-FEATURES, V-M-FRONTEND-FEATURES
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   useRemoveOffer - TanStack mutation
// END_MODULE_MAP
import { useMutation } from '@tanstack/react-query'

import { useInvalidateEditor } from '@/entities/campaign'
import { api, unwrap } from '@/shared/api'

export function useRemoveOffer(campaignId: number, streamId: number) {
  const invalidate = useInvalidateEditor(campaignId)
  return useMutation({
    mutationFn: async (offerId: number) =>
      unwrap(
        await api.DELETE('/api/campaigns/{campaign_id}/streams/{stream_id}/offers/{offer_id}', {
          params: { path: { campaign_id: campaignId, stream_id: streamId, offer_id: offerId } },
        }),
      ),
    onSettled: invalidate,
  })
}
