// START_MODULE_CONTRACT
//   PURPOSE: Application routes (react-router-dom) and the shared page layout.
//   SCOPE: / creator, /editor, /campaigns/:campaignId, legacy ?page= redirect, fallback to /.
//   DEPENDS: M-FRONTEND-PAGES, M-FRONTEND-WIDGETS
//   LINKS: M-FRONTEND-APP, V-M-FRONTEND-APP, V-M-FRONTEND-PAGES
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   paths     - URL builders for the app routes
//   AppRoutes - <Routes> tree with layout, pages and redirects
// END_MODULE_MAP
import { Navigate, Outlet, Route, Routes, useLocation, useNavigate, useParams } from 'react-router-dom'

import { CreateCampaignPage } from '@/pages/create-campaign'
import { OfferEditorPage } from '@/pages/offer-editor'
import { AppHeader } from '@/widgets/app-header'

export const paths = {
  create: () => '/',
  editor: () => '/editor',
  campaign: (campaignId: number) => `/campaigns/${campaignId}`,
}

function Layout() {
  return (
    <div className="min-h-svh">
      <AppHeader createPath={paths.create()} editorPath={paths.editor()} />
      <main className="mx-auto max-w-6xl px-4 py-6">
        <Outlet />
      </main>
    </div>
  )
}

function CreateRoute() {
  const navigate = useNavigate()
  return <CreateCampaignPage onOpenEditor={(id) => navigate(paths.campaign(id))} />
}

function EditorRoute() {
  const navigate = useNavigate()
  const { campaignId } = useParams()
  const id = campaignId && /^\d+$/.test(campaignId) ? Number(campaignId) : null
  if (campaignId !== undefined && id === null) return <Navigate to={paths.editor()} replace />
  return <OfferEditorPage campaignId={id} onSelectCampaign={(next) => navigate(paths.campaign(next))} />
}

// START_BLOCK_LEGACY_REDIRECT
// Old links looked like /?page=editor&campaign=214554 (before react-router); keep them working.
function IndexRoute() {
  const params = new URLSearchParams(useLocation().search)
  const page = params.get('page')
  const campaign = params.get('campaign')
  if (page === 'editor') {
    const to = campaign && /^\d+$/.test(campaign) ? paths.campaign(Number(campaign)) : paths.editor()
    return <Navigate to={to} replace />
  }
  if (page === 'create') return <Navigate to={paths.create()} replace />
  return <CreateRoute />
}
// END_BLOCK_LEGACY_REDIRECT

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<IndexRoute />} />
        <Route path="editor" element={<EditorRoute />} />
        <Route path="campaigns/:campaignId" element={<EditorRoute />} />
        <Route path="*" element={<Navigate to={paths.create()} replace />} />
      </Route>
    </Routes>
  )
}
