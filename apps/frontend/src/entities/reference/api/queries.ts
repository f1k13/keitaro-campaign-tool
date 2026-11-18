// START_MODULE_CONTRACT
//   PURPOSE: Query hooks for creator form selectors (domains, groups, traffic sources, defaults).
//   SCOPE: GET /api/reference/*.
//   DEPENDS: M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-ENTITIES, V-M-FRONTEND-ENTITIES
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   useDomains         - GET /api/reference/domains
//   useGroups          - GET /api/reference/groups
//   useTrafficSources  - GET /api/reference/traffic-sources
//   useCreatorDefaults - GET /api/reference/defaults
// END_MODULE_MAP
import { useQuery } from '@tanstack/react-query'

import { api, unwrap } from '@/shared/api'

const STALE = 5 * 60_000

export const useDomains = () =>
  useQuery({
    queryKey: ['reference', 'domains'],
    queryFn: async () => unwrap(await api.GET('/api/reference/domains')),
    staleTime: STALE,
  })

export const useGroups = () =>
  useQuery({
    queryKey: ['reference', 'groups'],
    queryFn: async () => unwrap(await api.GET('/api/reference/groups')),
    staleTime: STALE,
  })

export const useTrafficSources = () =>
  useQuery({
    queryKey: ['reference', 'traffic-sources'],
    queryFn: async () => unwrap(await api.GET('/api/reference/traffic-sources')),
    staleTime: STALE,
  })

export const useCreatorDefaults = () =>
  useQuery({
    queryKey: ['reference', 'defaults'],
    queryFn: async () => unwrap(await api.GET('/api/reference/defaults')),
    staleTime: Infinity,
  })
