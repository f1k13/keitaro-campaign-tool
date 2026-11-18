// START_MODULE_CONTRACT
//   PURPOSE: "Add offer" control: pick from offer list or enter an offer ID manually.
//   SCOPE: Popover UI + useAddOffer; toasts the result.
//   DEPENDS: M-FRONTEND-ENTITIES, M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-FEATURES, V-M-FRONTEND-FEATURES
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   AddOfferButton - excludes offers already in the stream
// END_MODULE_MAP
import { Loader2, Plus } from 'lucide-react'
import { useState } from 'react'
import { toast } from 'sonner'

import { useOffers } from '@/entities/offer'
import { Button } from '@/shared/ui/button'
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from '@/shared/ui/command'
import { Popover, PopoverContent, PopoverTrigger } from '@/shared/ui/popover'

import { useAddOffer } from '../model/useAddOffer'

export function AddOfferButton({
  campaignId,
  streamId,
  existing,
  disabled,
}: {
  campaignId: number
  streamId: number
  existing: number[]
  disabled?: boolean
}) {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const offers = useOffers()
  const add = useAddOffer(campaignId, streamId)

  const available = (offers.data ?? []).filter((o) => !existing.includes(o.id))
  const q = query.trim().toLowerCase()
  const filtered = available.filter((o) => !q || o.name.toLowerCase().includes(q) || String(o.id).includes(q))
  const manualId = /^\d+$/.test(query.trim()) ? Number(query.trim()) : null
  const showManual = manualId !== null && !existing.includes(manualId) && !available.some((o) => o.id === manualId)

  const submit = (offerId: number) => {
    setOpen(false)
    setQuery('')
    add.mutate(offerId, {
      onSuccess: () => toast.success(`Оффер ${offerId} добавлен, доли пересчитаны поровну`),
      onError: (e) => toast.error(e.message),
    })
  }

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button size="sm" disabled={disabled || add.isPending}>
          {add.isPending ? <Loader2 className="animate-spin" /> : <Plus />}
          Добавить оффер
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-96 p-0" align="end">
        <Command shouldFilter={false}>
          <CommandInput placeholder="Поиск по названию или ID оффера…" value={query} onValueChange={setQuery} />
          <CommandList>
            <CommandEmpty>{offers.isLoading ? 'Загрузка…' : 'Нет доступных офферов'}</CommandEmpty>
            {showManual && (
              <>
                <CommandGroup heading="По ID">
                  <CommandItem value={`manual-${manualId}`} onSelect={() => submit(manualId)}>
                    <Plus /> Добавить оффер #{manualId}
                  </CommandItem>
                </CommandGroup>
                <CommandSeparator />
              </>
            )}
            {filtered.length > 0 && (
              <CommandGroup heading="Офферы">
                {filtered.map((o) => (
                  <CommandItem key={o.id} value={String(o.id)} onSelect={() => submit(o.id)}>
                    <span className="w-14 font-mono text-xs text-muted-foreground">{o.id}</span>
                    <span className="truncate">{o.name}</span>
                  </CommandItem>
                ))}
              </CommandGroup>
            )}
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}
