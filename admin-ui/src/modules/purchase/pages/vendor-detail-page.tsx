import * as React from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import type { ColumnDef } from '@tanstack/react-table';
import { Button } from '@/components/ui/button';
import { DataTable } from '@/components/shared/data-table';
import { PageHeader } from '@/components/shared/page-header';
import { apiClient } from '@/lib/api/client';
import { usePurchaseList } from '../api/hooks';
import type { GRN, PurchaseInvoice, PurchaseOrder, Vendor, VendorLedgerEntry } from '../api/types';
import { StatusBadge } from '../components/purchase-list-page';
import { t } from '../lib/i18n';

type Tab = 'overview' | 'pos' | 'grns' | 'invoices' | 'ledger';

const TABS: Array<{ id: Tab; label: string }> = [
  { id: 'overview', label: 'Overview' },
  { id: 'pos', label: t('pos.title') },
  { id: 'grns', label: t('grns.title') },
  { id: 'invoices', label: t('invoices.title') },
  { id: 'ledger', label: t('ledger.title') },
];

export function VendorDetailPage() {
  const { id: idParam } = useParams<{ id: string }>();
  const id = Number(idParam);
  const navigate = useNavigate();
  const [tab, setTab] = React.useState<Tab>('overview');

  const { data: vendor, isLoading } = useQuery<Vendor, Error>({
    queryKey: ['purchase', 'vendor-detail', id],
    enabled: !!id,
    queryFn: async () => {
      const res = await apiClient.get<Vendor>(`/purchase/vendors/${id}/`);
      return res.data;
    },
  });

  if (isLoading || !vendor) {
    return <p className="text-sm text-muted-foreground">Loading…</p>;
  }

  return (
    <div className="space-y-4">
      <PageHeader
        title={`${vendor.code} — ${vendor.name}`}
        description={vendor.gstin ? `GSTIN: ${vendor.gstin}` : undefined}
        actions={
          <Button variant="outline" size="sm" onClick={() => navigate('/purchase/vendors')}>
            ← Back to list
          </Button>
        }
      />
      <div className="flex flex-wrap gap-1 border-b">
        {TABS.map((tb) => (
          <button
            key={tb.id}
            type="button"
            onClick={() => setTab(tb.id)}
            className={
              'border-b-2 px-3 py-1.5 text-sm ' +
              (tab === tb.id
                ? 'border-foreground font-medium'
                : 'border-transparent text-muted-foreground hover:text-foreground')
            }
          >
            {tb.label}
          </button>
        ))}
      </div>
      {tab === 'overview' && <OverviewTab vendor={vendor} />}
      {tab === 'pos' && <POsTab vendorId={id} />}
      {tab === 'grns' && <GRNsTab vendorId={id} />}
      {tab === 'invoices' && <InvoicesTab vendorId={id} />}
      {tab === 'ledger' && <LedgerTab vendorId={id} />}
    </div>
  );
}

function OverviewTab({ vendor }: { vendor: Vendor }) {
  return (
    <dl className="grid grid-cols-2 gap-3 text-sm md:grid-cols-3">
      <Pair label="Contact" value={vendor.contact_name || '—'} />
      <Pair label="Email" value={vendor.contact_email || '—'} />
      <Pair label="Mobile" value={vendor.contact_mobile || '—'} />
      <Pair label="PAN" value={vendor.pan || '—'} />
      <Pair label="Credit limit" value={vendor.credit_limit} />
      <Pair label="Status" value={vendor.is_active ? 'Active' : 'Inactive'} />
    </dl>
  );
}

function Pair({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="space-y-0.5">
      <dt className="text-xs text-muted-foreground">{label}</dt>
      <dd>{value}</dd>
    </div>
  );
}

function POsTab({ vendorId }: { vendorId: number }) {
  const { data } = usePurchaseList<PurchaseOrder>('pos', { vendor: vendorId });
  const cols: ColumnDef<PurchaseOrder, unknown>[] = [
    { accessorKey: 'po_no', header: () => t('po.no') },
    {
      id: 'status',
      header: () => t('common.status'),
      cell: ({ row }) => <StatusBadge value={row.original.status} />,
    },
    { accessorKey: 'expected_delivery', header: () => 'Expected' },
    {
      id: 'total',
      header: () => t('po.total'),
      cell: ({ row }) => row.original.totals_json?.grand_total ?? '0',
    },
  ];
  return <DataTable<PurchaseOrder, unknown> columns={cols} data={data ?? []} empty="No POs." />;
}

function GRNsTab({ vendorId }: { vendorId: number }) {
  const { data } = usePurchaseList<GRN>('grns', { vendor: vendorId });
  const cols: ColumnDef<GRN, unknown>[] = [
    { accessorKey: 'grn_no', header: () => t('grn.no') },
    {
      id: 'status',
      header: () => t('common.status'),
      cell: ({ row }) => <StatusBadge value={row.original.status} />,
    },
    { accessorKey: 'received_at', header: () => 'Received' },
  ];
  return <DataTable<GRN, unknown> columns={cols} data={data ?? []} empty="No GRNs." />;
}

function InvoicesTab({ vendorId }: { vendorId: number }) {
  const { data } = usePurchaseList<PurchaseInvoice>('invoices', { vendor: vendorId });
  const cols: ColumnDef<PurchaseInvoice, unknown>[] = [
    { accessorKey: 'pi_no', header: () => t('pi.no') },
    {
      id: 'status',
      header: () => t('common.status'),
      cell: ({ row }) => <StatusBadge value={row.original.status} />,
    },
    { accessorKey: 'invoice_date', header: () => t('pi.invoice_date') },
    { accessorKey: 'due_date', header: () => t('pi.due_date') },
  ];
  return (
    <DataTable<PurchaseInvoice, unknown> columns={cols} data={data ?? []} empty="No invoices." />
  );
}

function LedgerTab({ vendorId }: { vendorId: number }) {
  const { data } = usePurchaseList<VendorLedgerEntry>('ledger', { vendor: vendorId });
  const cols: ColumnDef<VendorLedgerEntry, unknown>[] = [
    { accessorKey: 'timestamp', header: () => 'When' },
    { accessorKey: 'reference_type', header: () => 'Type' },
    { accessorKey: 'reference_id', header: () => 'Ref' },
    { accessorKey: 'amount', header: () => 'Amount' },
    { accessorKey: 'balance_after', header: () => 'Balance' },
  ];
  return (
    <DataTable<VendorLedgerEntry, unknown>
      columns={cols}
      data={data ?? []}
      empty="No ledger entries."
    />
  );
}
