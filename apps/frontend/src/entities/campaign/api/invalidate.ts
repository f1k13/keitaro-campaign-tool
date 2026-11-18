// START_MODULE_CONTRACT
//   PURPOSE: Shared cache invalidation after any editor mutation.
//   SCOPE: Editor view (all intervals) and change log of one campaign.
//   DEPENDS: M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-ENTITIES, V-M-FRONTEND-ENTITIES
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   useInvalidateEditor - returns () => Promise invalidating editor queries of a campaign
// END_MODULE_MAP
import { useQueryClient } from '@tanstack/react-query'

import { campaignKeys } from './queries'

export function useInvalidateEditor(campaignId: number) {
  const qc = useQueryClient()
  return () =>
    Promise.all([
      qc.invalidateQueries({ queryKey: campaignKeys.editorAll(campaignId) }),
      qc.invalidateQueries({ queryKey: campaignKeys.changes(campaignId) }),
    ])
}
