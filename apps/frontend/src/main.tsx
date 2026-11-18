// START_MODULE_CONTRACT
//   PURPOSE: Browser entrypoint mounting the App.
//   SCOPE: React root + global styles.
//   DEPENDS: none
//   LINKS: M-FRONTEND-APP, V-M-FRONTEND-APP
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   (entrypoint) - mounts <App /> into #root; exports nothing
// END_MODULE_MAP
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import { App } from '@/app/App'
import '@/app/styles/index.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
