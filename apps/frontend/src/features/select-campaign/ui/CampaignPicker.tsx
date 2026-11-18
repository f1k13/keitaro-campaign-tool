// START_MODULE_CONTRACT
//   PURPOSE: Pick an existing Keitaro campaign by name, alias or id.
//   SCOPE: Search input with debounced query + popover results list.
//   DEPENDS: M-FRONTEND-ENTITIES, M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-FEATURES, V-M-FRONTEND-FEATURES
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   CampaignPicker - combobox calling onSelect(campaignId)
// END_MODULE_MAP
import { ChevronsUpDown } from 'lucide-react'
import { useEffect, useState } from 'react'

import { useCampaigns } from '@/entities/campaign'
import { Badge } from '@/shared/ui/badge'
import { Button } from '@/shared/ui/button'
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from '@/shared/ui/command'
import { Popover, PopoverContent, PopoverTrigger } from '@/shared/ui/popover'

function useDebounced<T>(value: T, ms = 300) {
  const [v, setV] = useState(value)
  useEffect(() => {
    const t = setTimeout(() => setV(value), ms)
    return () => clearTimeout(t)
  }, [value, ms])
  return v
}

export function CampaignPicker({
  selectedLabel,
  onSelect,
}: {
  selectedLabel: string | null
  onSelect: (id: number) => void
}) {
  const [open, setOpen] = useState(false)
  const [search, setSearch] = useState('')
  const debounced = useDebounced(search)
  const campaigns = useCampaigns(debounced)

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button variant="outline" role="combobox" className="w-full justify-between font-normal sm:w-[480px]">
          <span className="truncate">{selectedLabel ?? 'Выберите кампанию'}</span>
          <ChevronsUpDown className="opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-(--radix-popover-trigger-width) p-0" align="start">
        <Command shouldFilter={false}>
          <CommandInput placeholder="Название, alias или ID…" value={search} onValueChange={setSearch} />
          <CommandList>
            <CommandEmpty>{campaigns.isFetching ? 'Загрузка…' : 'Ничего не найдено'}</CommandEmpty>
            <CommandGroup>
              {campaigns.data?.map((c) => (
                <CommandItem
                  key={c.id}
                  value={String(c.id)}
                  onSelect={() => {
                    onSelect(c.id)
                    setOpen(false)
                  }}
                >
                  <span className="w-16 font-mono text-xs text-muted-foreground">{c.id}</span>
                  <span className="truncate">{c.name}</span>
                  {c.created_here && (
                    <Badge variant="secondary" className="ml-auto">
                      наша
                    </Badge>
                  )}
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}
