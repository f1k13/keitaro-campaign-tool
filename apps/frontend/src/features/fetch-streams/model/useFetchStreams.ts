// START_MODULE_CONTRACT
//   PURPOSE: Fetch Streams mutation: re-sync the campaign wrapper from Keitaro.
//   SCOPE: POST /api/campaigns/{cid}/streams/fetch + cache invalidation.
//   DEPENDS: M-FRONTEND-ENTITIES, M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-FEATURES, V-M-FRONTEND-FEATURES
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   fetchStreamsKey - mutation key (pages use it with useIsMutating to lock row actions)
//   useFetchStreams - TanStack mutation
// END_MODULE_MAP
import { useMutation } from '@tanstack/react-query'

import { useInvalidateEditor } from '@/entities/campaign'
import { api, unwrap } from '@/shared/api'

export const fetchStreamsKey = (campaignId: number) => ['fetch-streams', campaignId] as const

export function useFetchStreams(campaignId: number) {
  const invalidate = useInvalidateEditor(campaignId)
  return useMutation({
    mutationKey: fetchStreamsKey(campaignId),
    mutationFn: async () =>
      unwrap(
        await api.POST('/api/campaigns/{campaign_id}/streams/fetch', {
          params: { path: { campaign_id: campaignId } },
        }),
      ),
    onSettled: invalidate,
  })
}
