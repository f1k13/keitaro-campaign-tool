// START_MODULE_CONTRACT
//   PURPOSE: "Вернуть" (bring back) button for a removed offer.
//   SCOPE: Button + useRestoreOffer; toasts errors.
//   DEPENDS: M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-FEATURES, V-M-FRONTEND-FEATURES
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   RestoreOfferButton - small outline button
// END_MODULE_MAP
import { Loader2, Undo2 } from 'lucide-react'
import { toast } from 'sonner'

import { Button } from '@/shared/ui/button'

import { useRestoreOffer } from '../model/useRestoreOffer'

export function RestoreOfferButton({
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
  const restore = useRestoreOffer(campaignId, streamId)
  return (
    <Button
      size="sm"
      variant="outline"
      className="h-7"
      disabled={disabled || restore.isPending}
      onClick={() => restore.mutate(offerId, { onError: (e) => toast.error(e.message) })}
    >
      {restore.isPending ? <Loader2 className="animate-spin" /> : <Undo2 />}
      Вернуть
    </Button>
  )
}
