import * as React from 'react';
import type { ColumnDef } from '@tanstack/react-table';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { InventoryListPage, StatusBadge } from '../components/inventory-list-page';
import type { Batch } from '../api/types';
import { t } from '../lib/i18n';

export function BatchesPage() {
  const [branch, setBranch] = React.useState('');
  const [status, setStatus] = React.useState('');
  const params = React.useMemo(
    () => ({
      ...(branch && { branch: Number(branch) }),
      ...(status && { status }),
    }),
    [branch, status],
  );

  const columns: ColumnDef<Batch, unknown>[] = [
    { accessorKey: 'batch_no', header: () => 'Batch #' },
    { accessorKey: 'product', header: () => t('common.product') },
    { accessorKey: 'branch', header: () => t('common.branch') },
    { accessorKey: 'mfg_date', header: () => 'Mfg' },
    { accessorKey: 'expiry_date', header: () => 'Expiry' },
    { accessorKey: 'qty', header: () => t('common.qty') },
    { accessorKey: 'cost_price', header: () => 'Cost' },
    {
      accessorKey: 'status',
      header: () => t('common.status'),
      cell: ({ row }) => <StatusBadge value={row.original.status} />,
    },
  ];

  return (
    <InventoryListPage<Batch>
      endpoint="batches"
      title={t('batches.title')}
      subtitle="Batch-tracked inventory with shelf-life and cost."
      columns={columns}
      extraParams={params}
      filters={
        <>
          <div className="space-y-1">
            <Label className="text-xs" htmlFor="batches-branch">
              Branch ID
            </Label>
            <Input
              id="batches-branch"
              value={branch}
              onChange={(e) => setBranch(e.target.value.replace(/[^0-9]/g, ''))}
              className="h-9 w-28"
            />
          </div>
          <div className="space-y-1">
            <Label className="text-xs">{t('common.status')}</Label>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="h-9 rounded-md border border-input bg-background px-2 text-sm"
            >
              <option value="">—</option>
              <option value="ACTIVE">Active</option>
              <option value="EXPIRED">Expired</option>
              <option value="CONSUMED">Consumed</option>
            </select>
          </div>
        </>
      }
    />
  );
}
