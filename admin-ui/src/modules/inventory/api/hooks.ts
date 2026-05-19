import { useMutation, useQuery, useQueryClient, type UseQueryOptions } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import type { CursorPage, InventoryLedgerEntry, Paginated } from './types';

export type InventoryEndpoint =
  | 'stock'
  | 'batches'
  | 'ledger'
  | 'reservations'
  | 'transfers'
  | 'adjustments'
  | 'wastage'
  | 'counts';

export type ListParams = Record<string, string | number | boolean | undefined>;

export function inventoryKey(endpoint: InventoryEndpoint, params?: unknown): unknown[] {
  return ['inventory', endpoint, params ?? {}];
}

function buildSearch(params?: ListParams): string {
  const search = new URLSearchParams();
  for (const [k, v] of Object.entries(params ?? {})) {
    if (v == null || v === '') continue;
    search.set(k, String(v));
  }
  const qs = search.toString();
  return qs ? `?${qs}` : '';
}

async function fetchList<T>(endpoint: InventoryEndpoint, params?: ListParams): Promise<T[]> {
  const res = await apiClient.get<Paginated<T> | T[]>(
    `/inventory/${endpoint}/${buildSearch(params)}`,
  );
  return Array.isArray(res.data) ? res.data : (res.data.results ?? []);
}

export function useInventoryList<T>(
  endpoint: InventoryEndpoint,
  params?: ListParams,
  options?: Omit<UseQueryOptions<T[], Error>, 'queryKey' | 'queryFn'>,
) {
  return useQuery<T[], Error>({
    queryKey: inventoryKey(endpoint, params),
    queryFn: () => fetchList<T>(endpoint, params),
    ...options,
  });
}

export function useInventoryCreate<T, TInput = Partial<T>>(endpoint: InventoryEndpoint) {
  const qc = useQueryClient();
  return useMutation<T, Error, TInput>({
    mutationFn: async (values) => {
      const res = await apiClient.post<T>(`/inventory/${endpoint}/`, values);
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['inventory', endpoint] }),
  });
}

/** POST `/inventory/{endpoint}/{id}/{action}/`. */
export function useInventoryAction<T>(endpoint: InventoryEndpoint, action: string) {
  const qc = useQueryClient();
  return useMutation<T, Error, { id: number; body?: unknown }>({
    mutationFn: async ({ id, body }) => {
      const res = await apiClient.post<T>(`/inventory/${endpoint}/${id}/${action}/`, body ?? {});
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['inventory', endpoint] }),
  });
}

/**
 * Cursor-paginated ledger query. ``url`` overrides the endpoint when
 * provided (used for ``next``/``previous`` cursor URLs returned by
 * the backend — they're absolute API paths).
 */
export function useLedgerCursorPage(params: ListParams, url: string | null = null) {
  const qs = url ?? `/inventory/ledger/${buildSearch(params)}`;
  return useQuery<CursorPage<InventoryLedgerEntry>, Error>({
    queryKey: ['inventory', 'ledger', 'cursor', url ?? params],
    queryFn: async () => {
      const res = await apiClient.get<CursorPage<InventoryLedgerEntry>>(qs);
      return res.data;
    },
  });
}
