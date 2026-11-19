// START_MODULE_CONTRACT
//   PURPOSE: Application root: providers (router, query, toasts) around the route tree.
//   SCOPE: App layer of FSD.
//   DEPENDS: M-FRONTEND-PAGES, M-FRONTEND-WIDGETS, M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-APP, V-M-FRONTEND-APP
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   App - root component
// END_MODULE_MAP
import { BrowserRouter } from 'react-router-dom'

import { Toaster } from '@/shared/ui/sonner'

import { QueryProvider } from './query/QueryProvider'
import { AppRoutes } from './routing/AppRoutes'

export function App() {
  return (
    <BrowserRouter>
      <QueryProvider>
        <AppRoutes />
        <Toaster richColors position="top-right" />
      </QueryProvider>
    </BrowserRouter>
  )
}
