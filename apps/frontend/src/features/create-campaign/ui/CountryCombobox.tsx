// START_MODULE_CONTRACT
//   PURPOSE: Searchable country (geo) selector returning an ISO alpha-2 code.
//   SCOPE: Presentational + local open state.
//   DEPENDS: M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-FEATURES, V-M-FRONTEND-FEATURES
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   CountryCombobox - popover + command list over COUNTRIES
// END_MODULE_MAP
import { Check, ChevronsUpDown } from 'lucide-react'
import { useState } from 'react'

import { COUNTRIES } from '@/shared/config'
import { cn } from '@/shared/lib/utils'
import { Button } from '@/shared/ui/button'
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from '@/shared/ui/command'
import { Popover, PopoverContent, PopoverTrigger } from '@/shared/ui/popover'

export function CountryCombobox({ value, onChange }: { value: string; onChange: (code: string) => void }) {
  const [open, setOpen] = useState(false)
  const selected = COUNTRIES.find((c) => c.code === value)
  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button id="country" variant="outline" role="combobox" aria-expanded={open} className="w-full justify-between font-normal">
          {selected ? `${selected.code} — ${selected.name}` : 'Выберите страну'}
          <ChevronsUpDown className="opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-(--radix-popover-trigger-width) p-0" align="start">
        <Command>
          <CommandInput placeholder="Код или название…" />
          <CommandList>
            <CommandEmpty>Не найдено</CommandEmpty>
            <CommandGroup>
              {COUNTRIES.map((c) => (
                <CommandItem
                  key={c.code}
                  value={`${c.code} ${c.name}`}
                  onSelect={() => {
                    onChange(c.code)
                    setOpen(false)
                  }}
                >
                  <span className="w-8 font-mono text-xs text-muted-foreground">{c.code}</span>
                  {c.name}
                  <Check className={cn('ml-auto', value === c.code ? 'opacity-100' : 'opacity-0')} />
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}
