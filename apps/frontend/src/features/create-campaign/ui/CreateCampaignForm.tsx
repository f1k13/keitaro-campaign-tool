// START_MODULE_CONTRACT
//   PURPOSE: Campaign creator form: name (with server-side prefix preview), geo, offer (+ domain, group, source prefilled from defaults).
//   SCOPE: Form state, client validation, submit via useCreateCampaign.
//   DEPENDS: M-FRONTEND-ENTITIES, M-FRONTEND-SHARED
//   LINKS: M-FRONTEND-FEATURES, V-M-FRONTEND-FEATURES
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   CreateCampaignForm - renders the form, calls onCreated with the API result
// END_MODULE_MAP
import { Loader2 } from 'lucide-react'
import { useState, type FormEvent } from 'react'

import { useOffers } from '@/entities/offer'
import { useCreatorDefaults, useDomains, useGroups, useTrafficSources } from '@/entities/reference'
import type { Schemas } from '@/shared/api'
import { Alert, AlertDescription } from '@/shared/ui/alert'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/shared/ui/select'

import { useCreateCampaign } from '../model/useCreateCampaign'
import { CountryCombobox } from './CountryCombobox'

type Option = { id: number; name: string }

function IdSelect({
  id,
  label,
  value,
  onChange,
  options,
  loading,
}: {
  id: string
  label: string
  value: number | undefined
  onChange: (v: number) => void
  options: Option[] | undefined
  loading: boolean
}) {
  return (
    <div className="grid gap-2">
      <Label htmlFor={id}>{label}</Label>
      <Select value={value ? String(value) : undefined} onValueChange={(v) => onChange(Number(v))}>
        <SelectTrigger id={id} className="w-full">
          <SelectValue placeholder={loading ? 'Загрузка…' : 'Выберите'} />
        </SelectTrigger>
        <SelectContent>
          {options?.map((o) => (
            <SelectItem key={o.id} value={String(o.id)}>
              {o.name} <span className="text-muted-foreground">#{o.id}</span>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  )
}

export function CreateCampaignForm({ onCreated }: { onCreated: (c: Schemas['CampaignCreated']) => void }) {
  const offers = useOffers()
  const domains = useDomains()
  const groups = useGroups()
  const sources = useTrafficSources()
  const defaults = useCreatorDefaults()
  const create = useCreateCampaign()

  const [name, setName] = useState('')
  const [country, setCountry] = useState('')
  const [offerId, setOfferId] = useState<number>()
  // undefined = "use default from backend"
  const [domainId, setDomainId] = useState<number>()
  const [groupId, setGroupId] = useState<number>()
  const [sourceId, setSourceId] = useState<number>()

  const effective = {
    domain: domainId ?? defaults.data?.domain_id ?? undefined,
    group: groupId ?? defaults.data?.group_id ?? undefined,
    source: sourceId ?? defaults.data?.traffic_source_id ?? undefined,
  }
  const prefix = defaults.data?.campaign_name_prefix ?? ''
  // Same rule as backend apply_name_prefix: do not prefix twice.
  const fullName = !prefix || name.trim().startsWith(prefix) ? name.trim() : `${prefix}${name.trim()}`

  const canSubmit = name.trim() && country && offerId && effective.domain && effective.group && effective.source

  const submit = (e: FormEvent) => {
    e.preventDefault()
    if (!canSubmit) return
    create.mutate(
      {
        name: name.trim(),
        country,
        offer_id: offerId,
        domain_id: effective.domain,
        group_id: effective.group,
        traffic_source_id: effective.source,
      },
      {
        onSuccess: (created) => {
          onCreated(created)
          setName('')
        },
      },
    )
  }

  return (
    <form onSubmit={submit} className="grid gap-5">
      <div className="grid gap-2">
        <Label htmlFor="name">Название кампании</Label>
        <div className="flex">
          {prefix && (
            <span className="inline-flex items-center rounded-l-md border border-r-0 bg-muted px-3 font-mono text-sm text-muted-foreground">
              {prefix}
            </span>
          )}
          <Input
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="campaign1"
            className={prefix ? 'rounded-l-none' : undefined}
          />
        </div>
        {prefix && name.trim() && (
          <p className="text-xs text-muted-foreground">
            В Keitaro: <span className="font-mono">{fullName}</span>
          </p>
        )}
      </div>

      <div className="grid items-start gap-5 sm:grid-cols-2">
        <div className="grid gap-2">
          <Label htmlFor="country">Гео (страна)</Label>
          <CountryCombobox value={country} onChange={setCountry} />
          <p className="text-xs text-muted-foreground">Трафик из этой страны уйдёт на Google</p>
        </div>
        <IdSelect
          id="offer"
          label="Оффер"
          value={offerId}
          onChange={setOfferId}
          options={offers.data}
          loading={offers.isLoading}
        />
      </div>

      <div className="grid gap-5 sm:grid-cols-3">
        <IdSelect id="domain" label="Домен" value={effective.domain} onChange={setDomainId} options={domains.data} loading={domains.isLoading} />
        <IdSelect id="group" label="Группа" value={effective.group} onChange={setGroupId} options={groups.data} loading={groups.isLoading} />
        <IdSelect id="source" label="Источник" value={effective.source} onChange={setSourceId} options={sources.data} loading={sources.isLoading} />
      </div>

      {create.error && (
        <Alert variant="destructive">
          <AlertDescription>{create.error.message}</AlertDescription>
        </Alert>
      )}

      <div>
        <Button type="submit" disabled={!canSubmit || create.isPending}>
          {create.isPending && <Loader2 className="animate-spin" />}
          Создать кампанию
        </Button>
      </div>
    </form>
  )
}
