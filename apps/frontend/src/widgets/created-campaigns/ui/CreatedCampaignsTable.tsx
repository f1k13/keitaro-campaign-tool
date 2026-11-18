// START_MODULE_CONTRACT
//   PURPOSE: History of campaigns created through this tool (local PostgreSQL).
//   SCOPE: Read-only table with links to the editor.
//   DEPENDS: M-FRONTEND-ENTITIES, M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-WIDGETS, V-M-FRONTEND-WIDGETS
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   CreatedCampaignsTable - onEdit(campaignId) opens the editor
// END_MODULE_MAP
import { useCreatedCampaigns } from '@/entities/campaign'
import { Button } from '@/shared/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/shared/ui/table'

export function CreatedCampaignsTable({ onEdit }: { onEdit: (campaignId: number) => void }) {
  const created = useCreatedCampaigns()
  if (!created.data?.length) return null
  return (
    <Card>
      <CardHeader>
        <CardTitle>Созданные кампании</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>Название</TableHead>
              <TableHead>Гео</TableHead>
              <TableHead>Оффер</TableHead>
              <TableHead>Ссылка</TableHead>
              <TableHead />
            </TableRow>
          </TableHeader>
          <TableBody>
            {created.data.map((c) => (
              <TableRow key={c.keitaro_campaign_id}>
                <TableCell className="font-mono text-xs">{c.keitaro_campaign_id}</TableCell>
                <TableCell>{c.name}</TableCell>
                <TableCell>{c.country}</TableCell>
                <TableCell className="font-mono text-xs">#{c.offer_id}</TableCell>
                <TableCell>
                  {c.url && (
                    <a href={c.url} target="_blank" rel="noreferrer" className="text-sm underline underline-offset-4">
                      {c.url}
                    </a>
                  )}
                </TableCell>
                <TableCell className="text-right">
                  <Button size="sm" variant="outline" onClick={() => onEdit(c.keitaro_campaign_id)}>
                    Офферы
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}
