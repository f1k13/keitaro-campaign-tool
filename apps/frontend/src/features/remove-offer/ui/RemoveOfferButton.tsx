// START_MODULE_CONTRACT
//   PURPOSE: Remove-offer icon button (draft; no dialog - Cancel and bring back are the safety net).
//   SCOPE: Button + useRemoveOffer; toasts errors.
//   DEPENDS: M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-FEATURES, V-M-FRONTEND-FEATURES
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   RemoveOfferButton - trash icon button
// END_MODULE_MAP
import { Loader2, Trash2 } from 'lucide-react'
import { toast } from 'sonner'

import { Button } from '@/shared/ui/button'

import { useRemoveOffer } from '../model/useRemoveOffer'

export function RemoveOfferButton({
  campaignId,
  streamId,
  offerId,
  disabled,
}: {
  campaignId: number
  streamId: number
  offerId: number
  disabled?: boolean
}) {
  const remove = useRemoveOffer(campaignId, streamId)
  return (
    <Button
      variant="ghost"
      size="icon"
      aria-label="Удалить оффер"
      disabled={disabled || remove.isPending}
      onClick={() => remove.mutate(offerId, { onError: (e) => toast.error(e.message) })}
    >
      {remove.isPending ? <Loader2 className="animate-spin" /> : <Trash2 className="text-muted-foreground" />}
    </Button>
  )
}
