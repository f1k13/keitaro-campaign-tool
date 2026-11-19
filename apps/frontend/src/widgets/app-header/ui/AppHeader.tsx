// START_MODULE_CONTRACT
//   PURPOSE: Top bar with navigation links between the creator and the editor.
//   SCOPE: Presentational; active state from the current URL (editor is active on /editor and /campaigns/*).
//   DEPENDS: M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-WIDGETS, V-M-FRONTEND-WIDGETS
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   AppHeader - header with NavLinks; paths are passed in by the app layer
// END_MODULE_MAP
import { Link, useLocation } from 'react-router-dom'

import { cn } from '@/shared/lib/utils'

export function AppHeader({ createPath, editorPath }: { createPath: string; editorPath: string }) {
  const { pathname } = useLocation()
  const editorActive = pathname.startsWith(editorPath) || pathname.startsWith('/campaigns/')
  const items = [
    { to: createPath, label: 'Создать кампанию', active: !editorActive },
    { to: editorPath, label: 'Редактор офферов', active: editorActive },
  ]
  return (
    <header className="border-b bg-card">
      <div className="mx-auto flex max-w-6xl items-center gap-6 px-4 py-3">
        <Link to={createPath} className="font-semibold">
          Keitaro Tool
        </Link>
        <nav className="flex gap-1">
          {items.map((i) => (
            <Link
              key={i.to}
              to={i.to}
              aria-current={i.active ? 'page' : undefined}
              className={cn(
                'rounded-md px-3 py-1.5 text-sm transition-colors',
                i.active ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:bg-accent',
              )}
            >
              {i.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  )
}
