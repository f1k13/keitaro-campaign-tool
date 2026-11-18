// START_MODULE_CONTRACT
//   PURPOSE: Typed HTTP client generated from contracts/openapi.json.
//   SCOPE: openapi-fetch instance, error normalisation, schema type aliases.
//   DEPENDS: M-API-CONTRACT
//   LINKS: M-FRONTEND-SHARED, V-M-FRONTEND-SHARED
// END_MODULE_CONTRACT
//
// START_MODULE_MAP
//   api - openapi-fetch client (same-origin /api, proxied in dev and nginx)
//   ApiError - error carrying the backend `detail` message
//   unwrap - turns {data, error} into data or throws ApiError
//   Schemas - alias for components['schemas']
// END_MODULE_MAP
import createClient from 'openapi-fetch'

import type { components, paths } from './schema'

export type Schemas = components['schemas']

export const api = createClient<paths>({ baseUrl: '' })

export class ApiError extends Error {
  readonly status: number

  constructor(message: string, status: number) {
    super(message)
    this.status = status
  }
}

function messageOf(error: unknown): string {
  if (error && typeof error === 'object' && 'detail' in error) {
    const detail = (error as { detail: unknown }).detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) {
      return detail
        .map((d: { msg?: string; loc?: unknown[] }) => `${d.loc?.slice(1).join('.') ?? ''}: ${d.msg ?? ''}`)
        .join('; ')
    }
  }
  return 'Неизвестная ошибка сервера'
}

// START_CONTRACT: unwrap
//   PURPOSE: Convert openapi-fetch result into data or a thrown ApiError.
//   INPUTS: { result: { data?, error?, response } }
//   OUTPUTS: { T - response body }
//   SIDE_EFFECTS: throws ApiError on non-2xx
// END_CONTRACT: unwrap
export function unwrap<T>(result: { data?: T; error?: unknown; response: Response }): T {
  if (result.error !== undefined || !result.response.ok) {
    throw new ApiError(messageOf(result.error), result.response.status)
  }
  return result.data as T
}
