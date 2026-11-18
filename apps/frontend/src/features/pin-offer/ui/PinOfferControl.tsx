// START_MODULE_CONTRACT
//   PURPOSE: Pin control: unpinned -> popover with share input (default current share); pinned -> unpin.
//   SCOPE: Popover UI + usePinOffer / useUnpinOffer; toasts errors.
//   DEPENDS: M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-FEATURES, V-M-FRONTEND-FEATURES
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   PinOfferControl - pin icon button for one offer row
// END_MODULE_MAP
import { Loader2, Pin, PinOff } from 'lucide-react'
import { useState, type FormEvent } from 'react'
import { toast } from 'sonner'

import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import { Popover, PopoverContent, PopoverTrigger } from '@/shared/ui/popover'

import { usePinOffer, useUnpinOffer } from '../model/usePinOffer'

export function PinOfferControl({
  campaignId,
  streamId,
  offerId,
  share,
  pinned,
  disabled,
}: {
  campaignId: number
  streamId: number
  offerId: number
  share: number
  pinned: boolean
  disabled?: boolean
}) {
  const [open, setOpen] = useState(false)
  const [value, setValue] = useState(String(share))
  const pin = usePinOffer(campaignId, streamId, offerId)
  const unpin = useUnpinOffer(campaignId, streamId, offerId)
  const onError = (e: Error) => toast.error(e.message)

  if (pinned) {
    return (
      <Button
        variant="ghost"
        size="icon"
        aria-label="Открепить вес"
        title="Открепить вес"
        disabled={disabled || unpin.isPending}
        onClick={() => unpin.mutate(undefined, { onError })}
      >
        {unpin.isPending ? <Loader2 className="animate-spin" /> : <PinOff className="text-primary" />}
      </Button>
    )
  }

  const parsed = Number(value)
  const valid = value.trim() !== '' && Number.isInteger(parsed) && parsed >= 0 && parsed <= 100

  const submit = (e: FormEvent) => {
    e.preventDefault()
    if (!valid) return
    pin.mutate(parsed, { onSuccess: () => setOpen(false), onError })
  }

  return (
    <Popover
      open={open}
      onOpenChange={(o) => {
        setOpen(o)
        if (o) setValue(String(share))
      }}
    >
      <PopoverTrigger asChild>
        <Button variant="ghost" size="icon" aria-label="Запинить вес" title="Запинить вес" disabled={disabled}>
          <Pin className="text-muted-foreground" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-60" align="end">
        <form onSubmit={submit} className="grid gap-3">
          <Label htmlFor={`pin-${offerId}`}>Закрепить долю оффера #{offerId}</Label>
          <div className="flex items-center gap-2">
            <Input
              id={`pin-${offerId}`}
              type="number"
              min={0}
              max={100}
              step={1}
              value={value}
              onChange={(e) => setValue(e.target.value)}
              className="text-right tabular-nums"
              autoFocus
            />
            <span className="text-muted-foreground">%</span>
          </div>
          <Button type="submit" size="sm" disabled={!valid || pin.isPending}>
            {pin.isPending && <Loader2 className="animate-spin" />}
            Запинить
          </Button>
        </form>
      </PopoverContent>
    </Popover>
  )
}
