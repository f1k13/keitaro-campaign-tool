// START_MODULE_CONTRACT
//   PURPOSE: Draft mutation bringing back a removed offer.
//   SCOPE: POST /api/campaigns/{cid}/streams/{sid}/offers/{oid}/restore + cache invalidation.
//   DEPENDS: M-FRONTEND-ENTITIES, M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-FEATURES, V-M-FRONTEND-FEATURES
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   useRestoreOffer - TanStack mutation
// END_MODULE_MAP
import { useMutation } from '@tanstack/react-query'

import { useInvalidateEditor } from '@/entities/campaign'
import { api, unwrap } from '@/shared/api'

export function useRestoreOffer(campaignId: number, streamId: number) {
  const invalidate = useInvalidateEditor(campaignId)
  return useMutation({
    mutationFn: async (offerId: number) =>
      unwrap(
        await api.POST('/api/campaigns/{campaign_id}/streams/{stream_id}/offers/{offer_id}/restore', {
          params: { path: { campaign_id: campaignId, stream_id: streamId, offer_id: offerId } },
        }),
      ),
    onSettled: invalidate,
  })
}
