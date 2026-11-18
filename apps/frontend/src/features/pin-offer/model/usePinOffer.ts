// START_MODULE_CONTRACT
//   PURPOSE: Draft mutations pinning / unpinning an offer share.
//   SCOPE: PUT and DELETE /api/campaigns/{cid}/streams/{sid}/offers/{oid}/pin + cache invalidation.
//   DEPENDS: M-FRONTEND-ENTITIES, M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-FEATURES, V-M-FRONTEND-FEATURES
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   usePinOffer   - pin with a share value (null = current share)
//   useUnpinOffer - release the pin
// END_MODULE_MAP
import { useMutation } from '@tanstack/react-query'

import { useInvalidateEditor } from '@/entities/campaign'
import { api, unwrap } from '@/shared/api'

const PIN = '/api/campaigns/{campaign_id}/streams/{stream_id}/offers/{offer_id}/pin' as const

export function usePinOffer(campaignId: number, streamId: number, offerId: number) {
  const invalidate = useInvalidateEditor(campaignId)
  return useMutation({
    mutationFn: async (share: number | null) =>
      unwrap(
        await api.PUT(PIN, {
          params: { path: { campaign_id: campaignId, stream_id: streamId, offer_id: offerId } },
          body: { share },
        }),
      ),
    onSettled: invalidate,
  })
}

export function useUnpinOffer(campaignId: number, streamId: number, offerId: number) {
  const invalidate = useInvalidateEditor(campaignId)
  return useMutation({
    mutationFn: async () =>
      unwrap(
        await api.DELETE(PIN, {
          params: { path: { campaign_id: campaignId, stream_id: streamId, offer_id: offerId } },
        }),
      ),
    onSettled: invalidate,
  })
}
