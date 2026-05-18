import * as React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { cn } from '@/lib/utils';

interface Paginated<T> {
  count: number;
  results: T[];
}

interface RemoteSelectProps<T> {
  /** API path under `/api/v1/`, e.g. `purchase/vendors` or `master/branches`. */
  endpoint: string;
  /** Optional extra query params to pin the list (e.g. `{ status: 'APPROVED' }`). */
  params?: Record<string, string | number | undefined>;
  /** Build the user-visible label from a row. */
  labelFn: (row: T) => string;
  /** Pluck the id from a row. */
  idFn?: (row: T) => number;
  value: number | null | undefined;
  onChange: (v: number | null) => void;
  placeholder?: string;
  disabled?: boolean;
  id?: string;
  className?: string;
  'aria-invalid'?: boolean;
  'aria-describedby'?: string;
}

/**
 * Tiny dropdown that fetches a list from the API and lets the user pick one
 * by id. No async search yet — fine for the small lookup lists we have today
 * (branches, UoMs, vendors, products). Replace with a combobox when lists
 * grow large.
 */
export function RemoteSelect<T extends { id?: number }>(props: RemoteSelectProps<T>) {
  const {
    endpoint,
    params,
    labelFn,
    idFn = (r: T) => r.id as number,
    value,
    onChange,
    placeholder = '— Select —',
    disabled,
    id,
    className,
  } = props;
  const qs = React.useMemo(() => {
    const sp = new URLSearchParams();
    for (const [k, v] of Object.entries(params ?? {})) {
      if (v == null || v === '') continue;
      sp.set(k, String(v));
    }
    return sp.toString();
  }, [params]);
  const { data, isLoading } = useQuery<T[], Error>({
    queryKey: ['remote-select', endpoint, qs],
    queryFn: async () => {
      const url = `/${endpoint}/${qs ? `?${qs}` : ''}`;
      const res = await apiClient.get<Paginated<T> | T[]>(url);
      return Array.isArray(res.data) ? res.data : (res.data.results ?? []);
    },
    staleTime: 60_000,
  });
  return (
    <select
      id={id}
      className={cn('h-9 rounded-md border border-input bg-background px-2 text-sm', className)}
      value={value ?? ''}
      disabled={disabled || isLoading}
      aria-invalid={props['aria-invalid']}
      aria-describedby={props['aria-describedby']}
      onChange={(e) => {
        const raw = e.target.value;
        onChange(raw === '' ? null : Number(raw));
      }}
    >
      <option value="">{isLoading ? 'Loading…' : placeholder}</option>
      {(data ?? []).map((row) => (
        <option key={idFn(row)} value={idFn(row)}>
          {labelFn(row)}
        </option>
      ))}
    </select>
  );
}
