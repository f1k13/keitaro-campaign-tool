// START_MODULE_CONTRACT
//   PURPOSE: Mutation creating a campaign through POST /api/campaigns.
//   SCOPE: Invalidates campaign lists on success.
//   DEPENDS: M-FRONTEND-SHARED, M-FRONTEND-ENTITIES
//   LINKS: M-FRONTEND-FEATURES, V-M-FRONTEND-FEATURES
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   useCreateCampaign - TanStack mutation
// END_MODULE_MAP
import { useMutation, useQueryClient } from '@tanstack/react-query'

import { campaignKeys } from '@/entities/campaign'
import { api, unwrap, type Schemas } from '@/shared/api'

export function useCreateCampaign() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (body: Schemas['CampaignCreate']) => unwrap(await api.POST('/api/campaigns', { body })),
    onSuccess: () => qc.invalidateQueries({ queryKey: campaignKeys.all }),
  })
}
