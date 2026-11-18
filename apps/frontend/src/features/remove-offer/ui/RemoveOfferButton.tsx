// START_MODULE_CONTRACT
//   PURPOSE: Remove-offer button with an in-app confirmation dialog.
//   SCOPE: Dialog UI + useRemoveOffer; toasts the result.
//   DEPENDS: M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-FEATURES, V-M-FRONTEND-FEATURES
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   RemoveOfferButton - icon button + confirm dialog
// END_MODULE_MAP
import { Loader2, Trash2 } from 'lucide-react'
import { useState } from 'react'
import { toast } from 'sonner'

import { Button } from '@/shared/ui/button'
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/shared/ui/dialog'

import { useRemoveOffer } from '../model/useRemoveOffer'

export function RemoveOfferButton({
  campaignId,
  streamId,
  offerId,
  offerName,
  disabled,
}: {
  campaignId: number
  streamId: number
  offerId: number
  offerName: string
  disabled?: boolean
}) {
  const [open, setOpen] = useState(false)
  const remove = useRemoveOffer(campaignId, streamId)

  const confirm = () =>
    remove.mutate(offerId, {
      onSuccess: () => {
        setOpen(false)
        toast.success(`Оффер ${offerId} удалён из потока, доли пересчитаны поровну`)
      },
      onError: (e) => toast.error(e.message),
    })

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="icon" aria-label="Удалить оффер" disabled={disabled}>
          <Trash2 className="text-muted-foreground" />
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Удалить оффер из потока?</DialogTitle>
          <DialogDescription>
            «{offerName}» будет удалён, доли оставшихся активных офферов пересчитаются поровну.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline">Отмена</Button>
          </DialogClose>
          <Button variant="destructive" onClick={confirm} disabled={remove.isPending}>
            {remove.isPending && <Loader2 className="animate-spin" />}
            Удалить
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
