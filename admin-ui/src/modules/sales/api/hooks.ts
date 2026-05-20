import { useMutation, useQuery, useQueryClient, type UseQueryOptions } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import type { Discount, Paginated, Sale } from './types';

export type ListParams = Record<string, string | number | boolean | undefined>;

function buildSearch(params?: ListParams): string {
  const search = new URLSearchParams();
  for (const [k, v] of Object.entries(params ?? {})) {
    if (v == null || v === '') continue;
    search.set(k, String(v));
  }
  const qs = search.toString();
  return qs ? `?${qs}` : '';
}

async function fetchList<T>(endpoint: string, params?: ListParams): Promise<T[]> {
  const res = await apiClient.get<Paginated<T> | T[]>(`/${endpoint}/${buildSearch(params)}`);
  return Array.isArray(res.data) ? res.data : (res.data.results ?? []);
}

export function useSalesList(
  params?: ListParams,
  options?: Omit<UseQueryOptions<Sale[], Error>, 'queryKey' | 'queryFn'>,
) {
  return useQuery<Sale[], Error>({
    queryKey: ['sales', 'list', params ?? {}],
    queryFn: () => fetchList<Sale>('sales', params),
    ...options,
  });
}

export function useSaleDetail(id: number | string | undefined) {
  return useQuery<Sale, Error>({
    queryKey: ['sales', 'detail', id],
    enabled: id != null,
    queryFn: async () => {
      const res = await apiClient.get<Sale>(`/sales/${id}/`);
      return res.data;
    },
  });
}

export function useCreateSale() {
  const qc = useQueryClient();
  return useMutation<Sale, Error, Record<string, unknown>>({
    mutationFn: async (body) => {
      const res = await apiClient.post<Sale>('/sales/', body);
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['sales'] }),
  });
}

export function useSaleAction(action: 'post_sale' | 'cancel' | 'add_payment') {
  const qc = useQueryClient();
  return useMutation<Sale, Error, { id: number; body?: unknown }>({
    mutationFn: async ({ id, body }) => {
      const res = await apiClient.post<Sale>(`/sales/${id}/${action}/`, body ?? {});
      return res.data;
    },
    onSuccess: (_data, vars) => {
      qc.invalidateQueries({ queryKey: ['sales'] });
      qc.invalidateQueries({ queryKey: ['sales', 'detail', vars.id] });
    },
  });
}

export function useDiscountsList(
  params?: ListParams,
  options?: Omit<UseQueryOptions<Discount[], Error>, 'queryKey' | 'queryFn'>,
) {
  return useQuery<Discount[], Error>({
    queryKey: ['discounts', 'list', params ?? {}],
    queryFn: () => fetchList<Discount>('discounts', params),
    ...options,
  });
}
