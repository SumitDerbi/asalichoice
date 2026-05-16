import { useMutation, useQuery, useQueryClient, type UseQueryOptions } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import type { Paginated } from './types';

/**
 * Tuple of (endpoint, plural label). Endpoints are the trailing path
 * segment under `/api/v1/master/` (e.g. `branches`, `uom`).
 */
export type MasterEndpoint =
  | 'branches'
  | 'departments'
  | 'designations'
  | 'uom'
  | 'taxes'
  | 'hsn'
  | 'payment-modes'
  | 'categories'
  | 'brands'
  | 'warehouses'
  | 'zones'
  | 'countries'
  | 'states'
  | 'cities'
  | 'pincodes';

export type ListParams = Record<string, string | number | boolean | undefined>;

/** Builds a stable query key for TanStack Query caches. */
export function masterKey(endpoint: MasterEndpoint, params?: ListParams): unknown[] {
  return ['master', endpoint, params ?? {}];
}

async function fetchList<T>(endpoint: MasterEndpoint, params?: ListParams): Promise<T[]> {
  const search = new URLSearchParams();
  for (const [k, v] of Object.entries(params ?? {})) {
    if (v == null || v === '') continue;
    search.set(k, String(v));
  }
  const qs = search.toString();
  const url = `/master/${endpoint}/${qs ? `?${qs}` : ''}`;
  const res = await apiClient.get<Paginated<T> | T[]>(url);
  return Array.isArray(res.data) ? res.data : (res.data.results ?? []);
}

export function useMasterList<T>(
  endpoint: MasterEndpoint,
  params?: ListParams,
  options?: Omit<UseQueryOptions<T[], Error>, 'queryKey' | 'queryFn'>,
) {
  return useQuery<T[], Error>({
    queryKey: masterKey(endpoint, params),
    queryFn: () => fetchList<T>(endpoint, params),
    ...options,
  });
}

export function useMasterCreate<T, TInput = Partial<T>>(endpoint: MasterEndpoint) {
  const qc = useQueryClient();
  return useMutation<T, Error, TInput>({
    mutationFn: async (values) => {
      const res = await apiClient.post<T>(`/master/${endpoint}/`, values);
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['master', endpoint] }),
  });
}

export function useMasterUpdate<T, TInput = Partial<T>>(endpoint: MasterEndpoint) {
  const qc = useQueryClient();
  return useMutation<T, Error, { id: number; values: TInput }>({
    mutationFn: async ({ id, values }) => {
      const res = await apiClient.patch<T>(`/master/${endpoint}/${id}/`, values);
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['master', endpoint] }),
  });
}

/**
 * Soft-delete via DELETE — backend BaseModel.delete() flips `is_active`
 * and stamps `deleted_at`, so the resource is hidden from list responses
 * by default (`?include_inactive=true` to surface them).
 */
export function useMasterDelete(endpoint: MasterEndpoint) {
  const qc = useQueryClient();
  return useMutation<void, Error, number>({
    mutationFn: async (id) => {
      await apiClient.delete(`/master/${endpoint}/${id}/`);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['master', endpoint] }),
  });
}

/** Reactivate a soft-deleted row by PATCHing `is_active=true`. */
export function useMasterReactivate(endpoint: MasterEndpoint) {
  const qc = useQueryClient();
  return useMutation<void, Error, number>({
    mutationFn: async (id) => {
      await apiClient.patch(`/master/${endpoint}/${id}/`, { is_active: true });
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['master', endpoint] }),
  });
}
