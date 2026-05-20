import * as React from 'react';
import { Link } from 'react-router-dom';
import type { ColumnDef } from '@tanstack/react-table';
import { DataTable } from '@/components/shared/data-table';
import { PageHeader } from '@/components/shared/page-header';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useSalesList } from '../api/hooks';
import type { Sale, SaleOrigin, SaleStatus } from '../api/types';
import { t } from '../lib/i18n';

const STATUS_COLORS: Record<SaleStatus, string> = {
  DRAFT: 'bg-amber-50 text-amber-700',
  HELD: 'bg-zinc-100 text-zinc-700',
  CONFIRMED: 'bg-sky-50 text-sky-700',
  PARTIALLY_PAID: 'bg-blue-50 text-blue-700',
  PAID: 'bg-emerald-50 text-emerald-700',
  CANCELLED: 'bg-zinc-100 text-zinc-600',
  REFUNDED: 'bg-rose-50 text-rose-700',
};

function StatusBadge({ value }: { value: SaleStatus }) {
  const cls = STATUS_COLORS[value] ?? 'bg-zinc-100 text-zinc-700';
  return <span className={`rounded px-1.5 py-0.5 text-xs ${cls}`}>{value}</span>;
}

const ORIGINS: SaleOrigin[] = ['POS', 'ONLINE', 'B2B', 'MANUAL'];
const STATUSES: SaleStatus[] = [
  'DRAFT',
  'HELD',
  'CONFIRMED',
  'PARTIALLY_PAID',
  'PAID',
  'CANCELLED',
  'REFUNDED',
];

export function SalesListPage() {
  const [status, setStatus] = React.useState<string>('');
  const [origin, setOrigin] = React.useState<string>('');
  const [branch, setBranch] = React.useState('');
  const [cashier, setCashier] = React.useState('');
  const [customer, setCustomer] = React.useState('');
  const [dateFrom, setDateFrom] = React.useState('');
  const [dateTo, setDateTo] = React.useState('');

  const params = React.useMemo(
    () => ({
      ...(status && { status }),
      ...(origin && { origin }),
      ...(branch && { branch: Number(branch) }),
      ...(cashier && { cashier: Number(cashier) }),
      ...(customer && { customer: Number(customer) }),
      ...(dateFrom && { billed_at__gte: dateFrom }),
      ...(dateTo && { billed_at__lte: dateTo }),
    }),
    [status, origin, branch, cashier, customer, dateFrom, dateTo],
  );

  const { data, isLoading, isError, error, refetch } = useSalesList(params);

  const columns: ColumnDef<Sale, unknown>[] = [
    {
      accessorKey: 'sale_no',
      header: () => 'Sale #',
      cell: ({ row }) => (
        <Link to={`/sales/${row.original.id}`} className="text-primary underline">
          {row.original.sale_no}
        </Link>
      ),
    },
    { accessorKey: 'origin', header: () => t('common.origin') },
    {
      accessorKey: 'status',
      header: () => t('common.status'),
      cell: ({ row }) => <StatusBadge value={row.original.status} />,
    },
    { accessorKey: 'branch', header: () => t('common.branch') },
    { accessorKey: 'customer', header: () => t('common.customer') },
    { accessorKey: 'cashier', header: () => t('common.cashier') },
    {
      accessorKey: 'grand_total',
      header: () => t('common.grand_total'),
      cell: ({ row }) => Number(row.original.grand_total).toFixed(2),
    },
    {
      accessorKey: 'payment_total',
      header: () => t('common.payment_total'),
      cell: ({ row }) => Number(row.original.payment_total).toFixed(2),
    },
    {
      accessorKey: 'billed_at',
      header: () => t('common.created'),
      cell: ({ row }) =>
        row.original.billed_at
          ? new Date(row.original.billed_at).toLocaleString()
          : new Date(row.original.created_at).toLocaleString(),
    },
  ];

  return (
    <div className="space-y-4">
      <PageHeader
        title={t('sales.title')}
        description={t('sales.subtitle')}
        actions={
          <div className="flex gap-2">
            <Link
              to="/sales/new"
              className="rounded bg-primary px-3 py-1.5 text-sm text-primary-foreground"
            >
              {t('sales.new')}
            </Link>
            <Link to="/sales/b2b" className="rounded border px-3 py-1.5 text-sm">
              {t('sales.b2b')}
            </Link>
          </div>
        }
      />
      <div className="flex flex-wrap items-end gap-3">
        <div className="space-y-1">
          <Label className="text-xs" htmlFor="sales-status">
            Status
          </Label>
          <select
            id="sales-status"
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="h-9 rounded border px-2 text-sm"
          >
            <option value="">All</option>
            {STATUSES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>
        <div className="space-y-1">
          <Label className="text-xs" htmlFor="sales-origin">
            Origin
          </Label>
          <select
            id="sales-origin"
            value={origin}
            onChange={(e) => setOrigin(e.target.value)}
            className="h-9 rounded border px-2 text-sm"
          >
            <option value="">All</option>
            {ORIGINS.map((o) => (
              <option key={o} value={o}>
                {o}
              </option>
            ))}
          </select>
        </div>
        <div className="space-y-1">
          <Label className="text-xs" htmlFor="sales-branch">
            Branch ID
          </Label>
          <Input
            id="sales-branch"
            value={branch}
            onChange={(e) => setBranch(e.target.value.replace(/[^0-9]/g, ''))}
            className="h-9 w-24"
          />
        </div>
        <div className="space-y-1">
          <Label className="text-xs" htmlFor="sales-cashier">
            Cashier ID
          </Label>
          <Input
            id="sales-cashier"
            value={cashier}
            onChange={(e) => setCashier(e.target.value.replace(/[^0-9]/g, ''))}
            className="h-9 w-24"
          />
        </div>
        <div className="space-y-1">
          <Label className="text-xs" htmlFor="sales-customer">
            Customer ID
          </Label>
          <Input
            id="sales-customer"
            value={customer}
            onChange={(e) => setCustomer(e.target.value.replace(/[^0-9]/g, ''))}
            className="h-9 w-24"
          />
        </div>
        <div className="space-y-1">
          <Label className="text-xs" htmlFor="sales-from">
            From
          </Label>
          <Input
            id="sales-from"
            type="date"
            value={dateFrom}
            onChange={(e) => setDateFrom(e.target.value)}
            className="h-9 w-40"
          />
        </div>
        <div className="space-y-1">
          <Label className="text-xs" htmlFor="sales-to">
            To
          </Label>
          <Input
            id="sales-to"
            type="date"
            value={dateTo}
            onChange={(e) => setDateTo(e.target.value)}
            className="h-9 w-40"
          />
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
        <DataTable<Sale, unknown> columns={columns} data={data ?? []} empty={t('common.no_rows')} />
      )}
    </div>
  );
}
