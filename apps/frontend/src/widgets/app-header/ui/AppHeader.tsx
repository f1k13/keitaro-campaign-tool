// START_MODULE_CONTRACT
//   PURPOSE: Top bar with navigation between creator and editor pages.
//   SCOPE: Presentational.
//   DEPENDS: M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-WIDGETS, V-M-FRONTEND-WIDGETS
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   AppHeader - tabs-like nav
//   PageKey - 'create' | 'editor'
// END_MODULE_MAP
import { cn } from '@/shared/lib/utils'

export type PageKey = 'create' | 'editor'

const ITEMS: { key: PageKey; label: string }[] = [
  { key: 'create', label: 'Создать кампанию' },
  { key: 'editor', label: 'Редактор офферов' },
]

export function AppHeader({ page, onNavigate }: { page: PageKey; onNavigate: (p: PageKey) => void }) {
  return (
    <header className="border-b bg-card">
      <div className="mx-auto flex max-w-6xl items-center gap-6 px-4 py-3">
        <span className="font-semibold">Keitaro Tool</span>
        <nav className="flex gap-1">
          {ITEMS.map((i) => (
            <button
              key={i.key}
              type="button"
              onClick={() => onNavigate(i.key)}
              className={cn(
                'rounded-md px-3 py-1.5 text-sm transition-colors',
                page === i.key ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:bg-accent',
              )}
            >
              {i.label}
            </button>
          ))}
        </nav>
      </div>
    </header>
  )
}
