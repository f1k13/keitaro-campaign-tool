// START_MODULE_CONTRACT
//   PURPOSE: Push / Cancel buttons shown on a stream with an unpublished draft.
//   SCOPE: Buttons + usePushStream / useCancelStream; toasts results.
//   DEPENDS: M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-FEATURES, V-M-FRONTEND-FEATURES
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   PublishStreamActions - Cancel + Push
// END_MODULE_MAP
import { Loader2, Upload, X } from 'lucide-react'
import { toast } from 'sonner'

import { Button } from '@/shared/ui/button'

import { useCancelStream, usePushStream } from '../model/usePublishStream'

export function PublishStreamActions({
  campaignId,
  streamId,
  disabled,
}: {
  campaignId: number
  streamId: number
  disabled?: boolean
}) {
  const push = usePushStream(campaignId, streamId)
  const cancel = useCancelStream(campaignId, streamId)
  const busy = disabled || push.isPending || cancel.isPending
  return (
    <>
      <Button
        size="sm"
        variant="outline"
        disabled={busy}
        onClick={() =>
          cancel.mutate(undefined, {
            onSuccess: () => toast.success('Черновик отменён'),
            onError: (e) => toast.error(e.message),
          })
        }
      >
        {cancel.isPending ? <Loader2 className="animate-spin" /> : <X />}
        Cancel
      </Button>
      <Button
        size="sm"
        disabled={busy}
        onClick={() =>
          push.mutate(undefined, {
            onSuccess: () => toast.success('Опубликовано в Keitaro'),
            onError: (e) => toast.error(e.message),
          })
        }
      >
        {push.isPending ? <Loader2 className="animate-spin" /> : <Upload />}
        Push
      </Button>
    </>
  )
}
