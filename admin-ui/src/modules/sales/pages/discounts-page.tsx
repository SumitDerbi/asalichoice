import * as React from 'react';
import type { ColumnDef } from '@tanstack/react-table';
import { DataTable } from '@/components/shared/data-table';
import { PageHeader } from '@/components/shared/page-header';
import { useDiscountsList } from '../api/hooks';
import type { Discount } from '../api/types';
import { t } from '../lib/i18n';

export function DiscountsPage() {
  const [active, setActive] = React.useState<string>('');
  const params = React.useMemo(() => (active ? { is_active: active === 'yes' } : {}), [active]);
  const { data, isLoading, isError, error, refetch } = useDiscountsList(params);

  const columns: ColumnDef<Discount, unknown>[] = [
    { accessorKey: 'code', header: () => 'Code' },
    { accessorKey: 'name', header: () => 'Name' },
    { accessorKey: 'scope', header: () => 'Scope' },
    { accessorKey: 'kind', header: () => 'Kind' },
    {
      accessorKey: 'value',
      header: () => 'Value',
      cell: ({ row }) => Number(row.original.value).toFixed(2),
    },
    {
      accessorKey: 'is_active',
      header: () => 'Active',
      cell: ({ row }) => (row.original.is_active ? 'Yes' : 'No'),
    },
    {
      accessorKey: 'requires_approval',
      header: () => 'Needs approval',
      cell: ({ row }) => (row.original.requires_approval ? 'Yes' : 'No'),
    },
  ];

  return (
    <div className="space-y-4">
      <PageHeader title={t('discounts.title')} description={t('discounts.subtitle')} />
      <div className="flex flex-wrap items-end gap-3">
        <div className="space-y-1">
          <label className="text-xs" htmlFor="discount-active">
            Active
          </label>
          <select
            id="discount-active"
            value={active}
            onChange={(e) => setActive(e.target.value)}
            className="h-9 rounded border px-2 text-sm"
          >
            <option value="">All</option>
            <option value="yes">Yes</option>
            <option value="no">No</option>
          </select>
        </div>
      </div>
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
        <DataTable<Discount, unknown>
          columns={columns}
          data={data ?? []}
          empty={t('common.no_rows')}
        />
      )}
    </div>
  );
}
