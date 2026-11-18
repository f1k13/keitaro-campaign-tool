// START_MODULE_CONTRACT
//   PURPOSE: TanStack Query client provider.
//   SCOPE: Query defaults (no retry on 4xx, no refetch on focus).
//   DEPENDS: M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-APP, V-M-FRONTEND-APP
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   QueryProvider - wraps children with QueryClientProvider
// END_MODULE_MAP
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import type { ReactNode } from 'react'

import { ApiError } from '@/shared/api'

const client = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: (count, error) => !(error instanceof ApiError && error.status < 500) && count < 2,
    },
  },
})

export function QueryProvider({ children }: { children: ReactNode }) {
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>
}
