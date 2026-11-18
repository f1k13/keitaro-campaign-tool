// START_MODULE_CONTRACT
//   PURPOSE: TanStack Query hooks and keys for Keitaro campaigns.
//   SCOPE: Campaign list (search), locally created campaigns, editor view.
//   DEPENDS: M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-ENTITIES, V-M-FRONTEND-ENTITIES
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   StatsInterval       - report interval type
//   campaignKeys        - query key factory
//   useCampaigns        - GET /api/campaigns?search
//   useCreatedCampaigns - GET /api/campaigns/created
//   useEditorView       - GET /api/campaigns/{id}/editor?interval
//   useOfferChanges     - GET /api/campaigns/{id}/changes
// END_MODULE_MAP
import { keepPreviousData, useQuery } from '@tanstack/react-query'

import { api, unwrap, type Schemas } from '@/shared/api'

export type StatsInterval = Schemas['StatsInterval']

export const campaignKeys = {
  all: ['campaigns'] as const,
  list: (search: string) => ['campaigns', 'list', search] as const,
  created: ['campaigns', 'created'] as const,
  editor: (id: number, interval: StatsInterval) => ['campaigns', 'editor', id, interval] as const,
  editorAll: (id: number) => ['campaigns', 'editor', id] as const,
  changes: (id: number) => ['campaigns', 'changes', id] as const,
}

export function useCampaigns(search: string) {
  return useQuery({
    queryKey: campaignKeys.list(search),
    queryFn: async () =>
      unwrap(await api.GET('/api/campaigns', { params: { query: { search: search || undefined, limit: 50 } } })),
    placeholderData: keepPreviousData,
  })
}

export function useCreatedCampaigns() {
  return useQuery({
    queryKey: campaignKeys.created,
    queryFn: async () => unwrap(await api.GET('/api/campaigns/created')),
  })
}

export function useEditorView(campaignId: number | null, interval: StatsInterval) {
  return useQuery({
    queryKey: campaignKeys.editor(campaignId ?? 0, interval),
    queryFn: async () =>
      unwrap(
        await api.GET('/api/campaigns/{campaign_id}/editor', {
          params: { path: { campaign_id: campaignId! }, query: { interval } },
        }),
      ),
    enabled: campaignId !== null,
    placeholderData: keepPreviousData,
  })
}

export function useOfferChanges(campaignId: number | null) {
  return useQuery({
    queryKey: campaignKeys.changes(campaignId ?? 0),
    queryFn: async () =>
      unwrap(
        await api.GET('/api/campaigns/{campaign_id}/changes', { params: { path: { campaign_id: campaignId! } } }),
      ),
    enabled: campaignId !== null,
  })
}
