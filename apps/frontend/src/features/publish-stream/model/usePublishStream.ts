// START_MODULE_CONTRACT
//   PURPOSE: Push (publish draft to Keitaro) and Cancel (drop draft) mutations for one stream.
//   SCOPE: POST .../streams/{sid}/push and .../cancel + cache invalidation.
//   DEPENDS: M-FRONTEND-ENTITIES, M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-FEATURES, V-M-FRONTEND-FEATURES
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   usePushStream   - publish the draft
//   useCancelStream - restore the last published state
// END_MODULE_MAP
import { useMutation } from '@tanstack/react-query'

import { useInvalidateEditor } from '@/entities/campaign'
import { api, unwrap } from '@/shared/api'

export function usePushStream(campaignId: number, streamId: number) {
  const invalidate = useInvalidateEditor(campaignId)
  return useMutation({
    mutationFn: async () =>
      unwrap(
        await api.POST('/api/campaigns/{campaign_id}/streams/{stream_id}/push', {
          params: { path: { campaign_id: campaignId, stream_id: streamId } },
        }),
      ),
    onSettled: invalidate,
  })
}

export function useCancelStream(campaignId: number, streamId: number) {
  const invalidate = useInvalidateEditor(campaignId)
  return useMutation({
    mutationFn: async () =>
      unwrap(
        await api.POST('/api/campaigns/{campaign_id}/streams/{stream_id}/cancel', {
          params: { path: { campaign_id: campaignId, stream_id: streamId } },
        }),
      ),
    onSettled: invalidate,
  })
}
