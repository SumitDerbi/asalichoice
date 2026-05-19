import * as React from 'react';
import type { ColumnDef } from '@tanstack/react-table';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { DataTable } from '@/components/shared/data-table';
import { PageHeader } from '@/components/shared/page-header';
import { useLedgerCursorPage } from '../api/hooks';
import type { InventoryLedgerEntry } from '../api/types';
import { t } from '../lib/i18n';

const REF_TYPES = [
  'GRN',
  'SALE',
  'TRANSFER',
  'ADJUSTMENT',
  'RETURN',
  'WASTAGE',
  'OPENING',
  'COUNT',
];

export function LedgerPage() {
  const [branch, setBranch] = React.useState('');
  const [product, setProduct] = React.useState('');
  const [refType, setRefType] = React.useState('');
  const [reasonCode, setReasonCode] = React.useState('');
  const [cursor, setCursor] = React.useState<string | null>(null);

  // Reset to first page whenever filters change.
  const filterParams = React.useMemo(() => {
    const p: Record<string, string | number> = { page_size: 50 };
    if (branch) p.branch = Number(branch);
    if (product) p.product = Number(product);
    if (refType) p.ref_type = refType;
    if (reasonCode) p.reason_code = reasonCode;
    return p;
  }, [branch, product, refType, reasonCode]);

  React.useEffect(() => {
    setCursor(null);
  }, [branch, product, refType, reasonCode]);

  const { data, isLoading, isError, error } = useLedgerCursorPage(filterParams, cursor);

  const columns: ColumnDef<InventoryLedgerEntry, unknown>[] = [
    { accessorKey: 'timestamp', header: () => t('ledger.timestamp') },
    { accessorKey: 'reference_type', header: () => t('ledger.ref_type') },
    { accessorKey: 'reference_id', header: () => t('ledger.ref_id') },
    { accessorKey: 'branch', header: () => t('common.branch') },
    { accessorKey: 'product', header: () => t('common.product') },
    { accessorKey: 'amount', header: () => t('ledger.amount') },
    { accessorKey: 'balance_before', header: () => t('ledger.balance_before') },
    { accessorKey: 'balance_after', header: () => t('ledger.balance_after') },
    { accessorKey: 'reason_code', header: () => t('ledger.reason_code') },
    { accessorKey: 'actor', header: () => t('ledger.actor') },
  ];

  return (
    <div className="space-y-4">
      <PageHeader title={t('ledger.title')} description="Immutable, append-only stock movements." />
      <div className="flex flex-wrap items-end gap-3">
        <div className="space-y-1">
          <Label className="text-xs" htmlFor="led-branch">
            Branch ID
          </Label>
          <Input
            id="led-branch"
            value={branch}
            onChange={(e) => setBranch(e.target.value.replace(/[^0-9]/g, ''))}
            className="h-9 w-24"
          />
        </div>
        <div className="space-y-1">
          <Label className="text-xs" htmlFor="led-prod">
            Product ID
          </Label>
          <Input
            id="led-prod"
            value={product}
            onChange={(e) => setProduct(e.target.value.replace(/[^0-9]/g, ''))}
            className="h-9 w-24"
          />
        </div>
        <div className="space-y-1">
          <Label className="text-xs">{t('ledger.ref_type')}</Label>
          <select
            value={refType}
            onChange={(e) => setRefType(e.target.value)}
            className="h-9 rounded-md border border-input bg-background px-2 text-sm"
          >
            <option value="">—</option>
            {REF_TYPES.map((rt) => (
              <option key={rt} value={rt}>
                {rt}
              </option>
            ))}
          </select>
        </div>
        <div className="space-y-1">
          <Label className="text-xs" htmlFor="led-reason">
            {t('ledger.reason_code')}
          </Label>
          <Input
            id="led-reason"
            value={reasonCode}
            onChange={(e) => setReasonCode(e.target.value)}
            className="h-9 w-32"
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
        <p className="text-sm text-destructive">{(error as Error)?.message ?? t('common.error')}</p>
      ) : (
        <>
          <DataTable<InventoryLedgerEntry, unknown>
            columns={columns}
            data={data?.results ?? []}
            empty={t('common.no_rows')}
          />
          <div className="flex justify-between text-xs">
            <Button
              type="button"
              variant="outline"
              size="sm"
              disabled={!data?.previous}
              onClick={() => setCursor(data?.previous ?? null)}
            >
              ← {t('common.prev')}
            </Button>
            <Button
              type="button"
              variant="outline"
              size="sm"
              disabled={!data?.next}
              onClick={() => setCursor(data?.next ?? null)}
            >
              {t('common.next')} →
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
