import * as React from 'react';
import type { ColumnDef } from '@tanstack/react-table';
import { DataTable } from '@/components/shared/data-table';
import { PageHeader } from '@/components/shared/page-header';
import { useInventoryList, type InventoryEndpoint, type ListParams } from '../api/hooks';
import { t } from '../lib/i18n';

interface InventoryListPageProps<TRow> {
  endpoint: InventoryEndpoint;
  title: string;
  subtitle?: string;
  columns: ColumnDef<TRow, unknown>[];
  filters?: React.ReactNode;
  extraParams?: ListParams;
  actions?: React.ReactNode;
}

export function InventoryListPage<TRow extends { id: number | string }>(
  props: InventoryListPageProps<TRow>,
) {
  const { endpoint, title, subtitle, columns, filters, extraParams, actions } = props;
  const { data, isLoading, isError, error, refetch } = useInventoryList<TRow>(
    endpoint,
    extraParams,
  );

  return (
    <div className="space-y-4">
      <PageHeader title={title} description={subtitle} actions={actions} />
      {filters ? <div className="flex flex-wrap items-end gap-3">{filters}</div> : null}
      {isLoading ? (
        <div className="space-y-2" aria-label="Loading">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-9 animate-pulse rounded bg-muted/50" />
          ))}
        </div>
      ) : isError ? (
        <div className="space-y-2">
          <p className="text-sm text-destructive">
            {(error as Error)?.message ?? t('common.error')}
          </p>
          <button
            type="button"
            onClick={() => refetch()}
            className="text-xs text-primary underline"
          >
            {t('common.refresh')}
          </button>
        </div>
      ) : (
        <DataTable<TRow, unknown> columns={columns} data={data ?? []} empty={t('common.no_rows')} />
      )}
    </div>
  );
}

const STATUS_COLORS: Record<string, string> = {
  ACTIVE: 'bg-emerald-50 text-emerald-700',
  EXPIRED: 'bg-rose-50 text-rose-700',
  CONSUMED: 'bg-zinc-100 text-zinc-600',
  RELEASED: 'bg-zinc-100 text-zinc-600',
  DRAFT: 'bg-amber-50 text-amber-700',
  IN_TRANSIT: 'bg-blue-50 text-blue-700',
  RECEIVED: 'bg-emerald-50 text-emerald-700',
  PART_RECEIVED: 'bg-sky-50 text-sky-700',
  POSTED: 'bg-emerald-50 text-emerald-700',
  COUNTED: 'bg-sky-50 text-sky-700',
  CANCELLED: 'bg-zinc-100 text-zinc-600',
};

export function StatusBadge({ value }: { value: string }) {
  const cls = STATUS_COLORS[value] ?? 'bg-zinc-100 text-zinc-700';
  return <span className={`rounded px-1.5 py-0.5 text-xs ${cls}`}>{value}</span>;
}
