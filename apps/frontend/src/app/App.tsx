// START_MODULE_CONTRACT
//   PURPOSE: Application root: providers, header navigation, page switch via URL (?page=&campaign=).
//   SCOPE: App layer of FSD.
//   DEPENDS: M-FRONTEND-PAGES, M-FRONTEND-WIDGETS, M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-APP, V-M-FRONTEND-APP
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   App - root component
// END_MODULE_MAP
import { CreateCampaignPage } from '@/pages/create-campaign'
import { OfferEditorPage } from '@/pages/offer-editor'
import { AppHeader, type PageKey } from '@/widgets/app-header'
import { useUrlParam } from '@/shared/lib/url-state'
import { Toaster } from '@/shared/ui/sonner'

import { QueryProvider } from './query/QueryProvider'

export function App() {
  const [pageParam, setPage] = useUrlParam('page')
  const [campaignParam, setCampaign] = useUrlParam('campaign')
  const page: PageKey = pageParam === 'editor' ? 'editor' : 'create'
  const campaignId = campaignParam && /^\d+$/.test(campaignParam) ? Number(campaignParam) : null

  const openEditor = (id: number) => {
    setCampaign(String(id))
    setPage('editor')
  }

  return (
    <QueryProvider>
      <div className="min-h-svh">
        <AppHeader page={page} onNavigate={(p) => setPage(p)} />
        <main className="mx-auto max-w-6xl px-4 py-6">
          {page === 'create' ? (
            <CreateCampaignPage onOpenEditor={openEditor} />
          ) : (
            <OfferEditorPage campaignId={campaignId} onSelectCampaign={(id) => setCampaign(String(id))} />
          )}
        </main>
      </div>
      <Toaster richColors position="top-right" />
    </QueryProvider>
  )
}
