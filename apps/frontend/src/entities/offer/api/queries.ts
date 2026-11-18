// START_MODULE_CONTRACT
//   PURPOSE: Query hook for Keitaro offers available to the API key.
//   SCOPE: GET /api/reference/offers.
//   DEPENDS: M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-ENTITIES, V-M-FRONTEND-ENTITIES
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   useOffers - list of offers, cached 5 min
// END_MODULE_MAP
import { useQuery } from '@tanstack/react-query'

import { api, unwrap } from '@/shared/api'

export function useOffers() {
  return useQuery({
    queryKey: ['reference', 'offers'],
    queryFn: async () => unwrap(await api.GET('/api/reference/offers')),
    staleTime: 5 * 60_000,
  })
}
