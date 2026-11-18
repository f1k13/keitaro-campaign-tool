// START_MODULE_CONTRACT
//   PURPOSE: "Fetch Streams" button pulling the campaign streams from Keitaro.
//   SCOPE: Button + useFetchStreams; toasts results.
//   DEPENDS: M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-FEATURES, V-M-FRONTEND-FEATURES
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   FetchStreamsButton - outline button with spinner
// END_MODULE_MAP
import { Download, Loader2 } from 'lucide-react'
import { toast } from 'sonner'

import { Button } from '@/shared/ui/button'

import { useFetchStreams } from '../model/useFetchStreams'

export function FetchStreamsButton({ campaignId }: { campaignId: number }) {
  const fetchStreams = useFetchStreams(campaignId)
  return (
    <Button
      variant="outline"
      disabled={fetchStreams.isPending}
      onClick={() =>
        fetchStreams.mutate(undefined, {
          onSuccess: () => toast.success('Потоки обновлены из Keitaro'),
          onError: (e) => toast.error(e.message),
        })
      }
    >
      {fetchStreams.isPending ? <Loader2 className="animate-spin" /> : <Download />}
      Fetch Streams
    </Button>
  )
}
