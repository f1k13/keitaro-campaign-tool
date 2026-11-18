// START_MODULE_CONTRACT
//   PURPOSE: Minimal URL query-string state (page, campaign id) without a router dependency.
//   SCOPE: Read/write window.location.search, notify subscribers on popstate.
//   DEPENDS: none
//   LINKS: M-FRONTEND-SHARED, V-M-FRONTEND-SHARED
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   useUrlParam - [value, setValue] bound to one query param
// END_MODULE_MAP
import { useCallback, useSyncExternalStore } from 'react'

const EVENT = 'urlstatechange'

function subscribe(cb: () => void) {
  window.addEventListener('popstate', cb)
  window.addEventListener(EVENT, cb)
  return () => {
    window.removeEventListener('popstate', cb)
    window.removeEventListener(EVENT, cb)
  }
}

export function useUrlParam(name: string): [string | null, (value: string | null) => void] {
  const value = useSyncExternalStore(subscribe, () => new URLSearchParams(window.location.search).get(name))
  const set = useCallback(
    (next: string | null) => {
      const params = new URLSearchParams(window.location.search)
      if (next === null) params.delete(name)
      else params.set(name, next)
      const qs = params.toString()
      window.history.pushState(null, '', qs ? `?${qs}` : window.location.pathname)
      window.dispatchEvent(new Event(EVENT))
    },
    [name],
  )
  return [value, set]
}
