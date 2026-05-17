import { useMutation, useQuery, useQueryClient, type UseQueryOptions } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import type { Paginated } from './types';

export type CatalogEndpoint =
  | 'products'
  | 'variants'
  | 'images'
  | 'availability'
  | 'prices'
  | 'bundles'
  | 'bundle-components'
  | 'barcodes'
  | 'attributes'
  | 'attribute-values';

export type ListParams = Record<string, string | number | boolean | undefined>;

export function catalogKey(endpoint: CatalogEndpoint, params?: ListParams): unknown[] {
  return ['catalog', endpoint, params ?? {}];
}

async function fetchList<T>(endpoint: CatalogEndpoint, params?: ListParams): Promise<T[]> {
  const search = new URLSearchParams();
  for (const [k, v] of Object.entries(params ?? {})) {
    if (v == null || v === '') continue;
    search.set(k, String(v));
  }
  const qs = search.toString();
  const url = `/catalog/${endpoint}/${qs ? `?${qs}` : ''}`;
  const res = await apiClient.get<Paginated<T> | T[]>(url);
  return Array.isArray(res.data) ? res.data : (res.data.results ?? []);
}

export function useCatalogList<T>(
  endpoint: CatalogEndpoint,
  params?: ListParams,
  options?: Omit<UseQueryOptions<T[], Error>, 'queryKey' | 'queryFn'>,
) {
  return useQuery<T[], Error>({
    queryKey: catalogKey(endpoint, params),
    queryFn: () => fetchList<T>(endpoint, params),
    ...options,
  });
}

export function useCatalogCreate<T, TInput = Partial<T>>(endpoint: CatalogEndpoint) {
  const qc = useQueryClient();
  return useMutation<T, Error, TInput>({
    mutationFn: async (values) => {
      const res = await apiClient.post<T>(`/catalog/${endpoint}/`, values);
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['catalog', endpoint] }),
  });
}

export function useCatalogUpdate<T, TInput = Partial<T>>(endpoint: CatalogEndpoint) {
  const qc = useQueryClient();
  return useMutation<T, Error, { id: number; values: TInput }>({
    mutationFn: async ({ id, values }) => {
      const res = await apiClient.patch<T>(`/catalog/${endpoint}/${id}/`, values);
      return res.data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['catalog', endpoint] }),
  });
}

export function useCatalogDelete(endpoint: CatalogEndpoint) {
  const qc = useQueryClient();
  return useMutation<void, Error, number>({
    mutationFn: async (id) => {
      await apiClient.delete(`/catalog/${endpoint}/${id}/`);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['catalog', endpoint] }),
  });
}

export function useArchiveProduct() {
  const qc = useQueryClient();
  return useMutation<void, Error, number>({
    mutationFn: async (id) => {
      await apiClient.post(`/catalog/products/${id}/archive/`);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['catalog', 'products'] }),
  });
}

export interface ImportResponse {
  total: number;
  created: number;
  valid: number;
  committed: boolean;
  errors: Array<{ row: number; error: string; data: Record<string, string> }>;
}

export function useImportProducts() {
  const qc = useQueryClient();
  return useMutation<ImportResponse, Error, { file: File; dryRun: boolean }>({
    mutationFn: async ({ file, dryRun }) => {
      const fd = new FormData();
      fd.append('file', file);
      if (!dryRun) fd.append('dry_run', 'false');
      else fd.append('dry_run', 'true');
      const res = await apiClient.post<ImportResponse>(`/catalog/import/`, fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return res.data;
    },
    onSuccess: (data) => {
      if (data.committed) qc.invalidateQueries({ queryKey: ['catalog', 'products'] });
    },
  });
}
