import * as React from 'react';
import type { ColumnDef } from '@tanstack/react-table';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { DataTable } from '@/components/shared/data-table';
import { PageHeader } from '@/components/shared/page-header';
import { usePurchaseList } from '../api/hooks';
import type { VendorLedgerEntry } from '../api/types';
import { t } from '../lib/i18n';

export function LedgerPage() {
  const [vendorId, setVendorId] = React.useState('');
  const params = vendorId ? { vendor: Number(vendorId) } : undefined;
  const { data, isLoading, isError, error } = usePurchaseList<VendorLedgerEntry>('ledger', params);

  const columns: ColumnDef<VendorLedgerEntry, unknown>[] = [
    { accessorKey: 'timestamp', header: () => t('ledger.timestamp') },
    { accessorKey: 'reference_type', header: () => 'Ref. type' },
    { accessorKey: 'reference_id', header: () => 'Ref. id' },
    { accessorKey: 'amount', header: () => t('ledger.amount') },
    { accessorKey: 'balance_after', header: () => t('ledger.balance') },
    { accessorKey: 'remarks', header: () => 'Remarks' },
  ];

  return (
    <div className="space-y-4">
      <PageHeader title={t('ledger.title')} description="Immutable vendor postings." />
      <div className="flex items-end gap-3">
        <div className="space-y-1">
          <Label className="text-xs" htmlFor="ledger-vendor">
            Vendor ID
          </Label>
          <Input
            id="ledger-vendor"
            value={vendorId}
            onChange={(e) => setVendorId(e.target.value.replace(/[^0-9]/g, ''))}
            className="h-9 w-32"
            placeholder="e.g. 1"
          />
        </div>
      </div>
      {isLoading ? (
        <div className="space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-9 animate-pulse rounded bg-muted/50" />
          ))}
        </div>
      ) : isError ? (
        <p className="text-sm text-destructive">{(error as Error)?.message ?? t('common.error')}</p>
      ) : (
        <DataTable<VendorLedgerEntry, unknown>
          columns={columns}
          data={data ?? []}
          empty="No ledger entries."
        />
      )}
    </div>
  );
}
