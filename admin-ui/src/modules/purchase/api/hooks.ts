import { useMutation, useQuery, useQueryClient, type UseQueryOptions } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import type { Paginated } from './types';

export type PurchaseEndpoint = 'vendors' | 'pos' | 'grns' | 'invoices' | 'returns' | 'ledger';

export type ListParams = Record<string, string | number | boolean | undefined>;

export function purchaseKey(endpoint: PurchaseEndpoint, params?: ListParams): unknown[] {
  return ['purchase', endpoint, params ?? {}];
}

async function fetchList<T>(endpoint: PurchaseEndpoint, params?: ListParams): Promise<T[]> {
  const search = new URLSearchParams();
  for (const [k, v] of Object.entries(params ?? {})) {
    if (v == null || v === '') continue;
    search.set(k, String(v));
  }
  const qs = search.toString();
  const url = `/purchase/${endpoint}/${qs ? `?${qs}` : ''}`;
  const res = await apiClient.get<Paginated<T> | T[]>(url);
  return Array.isArray(res.data) ? res.data : (res.data.results ?? []);
}

export function usePurchaseList<T>(
  endpoint: PurchaseEndpoint,
  params?: ListParams,
  options?: Omit<UseQueryOptions<T[], Error>, 'queryKey' | 'queryFn'>,
) {
  return useQuery<T[], Error>({
    queryKey: purchaseKey(endpoint, params),
    queryFn: () => fetchList<T>(endpoint, params),
    ...options,
  });
}

export function usePurchaseCreate<T, TInput = Partial<T>>(endpoint: PurchaseEndpoint) {
  const qc = useQueryClient();
  return useMutation<T, Error, TInput>({
    mutationFn: async (values) => {
      const res = await apiClient.post<T>(`/purchase/${endpoint}/`, values);
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['purchase', endpoint] }),
  });
}

export function usePurchaseUpdate<T, TInput = Partial<T>>(endpoint: PurchaseEndpoint) {
  const qc = useQueryClient();
  return useMutation<T, Error, { id: number; values: TInput }>({
    mutationFn: async ({ id, values }) => {
      const res = await apiClient.patch<T>(`/purchase/${endpoint}/${id}/`, values);
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['purchase', endpoint] }),
  });
}

export function usePurchaseDelete(endpoint: PurchaseEndpoint) {
  const qc = useQueryClient();
  return useMutation<void, Error, number>({
    mutationFn: async (id) => {
      await apiClient.delete(`/purchase/${endpoint}/${id}/`);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['purchase', endpoint] }),
  });
}

/** Generic POST-action invoker (no body): `/purchase/{endpoint}/{id}/{action}/`. */
export function usePurchaseAction<T>(endpoint: PurchaseEndpoint, action: string) {
  const qc = useQueryClient();
  return useMutation<T, Error, { id: number; body?: unknown }>({
    mutationFn: async ({ id, body }) => {
      const res = await apiClient.post<T>(`/purchase/${endpoint}/${id}/${action}/`, body ?? {});
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['purchase', endpoint] }),
  });
}

/** Collection-level POST action (e.g. invoices/from-grns, grns/sync-offline). */
export function usePurchaseCollectionAction<T, TBody = unknown>(
  endpoint: PurchaseEndpoint,
  action: string,
) {
  const qc = useQueryClient();
  return useMutation<T, Error, TBody>({
    mutationFn: async (body) => {
      const res = await apiClient.post<T>(`/purchase/${endpoint}/${action}/`, body);
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['purchase', endpoint] }),
  });
}
