import * as React from 'react';
import type { ColumnDef } from '@tanstack/react-table';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { ApiError } from '@/lib/api/errors';
import { InventoryListPage, StatusBadge } from '../components/inventory-list-page';
import { useInventoryAction } from '../api/hooks';
import { useCanTransfer } from '../lib/use-permission';
import type { BranchTransfer } from '../api/types';
import { t } from '../lib/i18n';

export function TransfersPage() {
  const canTransfer = useCanTransfer();
  const dispatchMut = useInventoryAction<BranchTransfer>('transfers', 'dispatch');
  const receiveMut = useInventoryAction<BranchTransfer>('transfers', 'receive');
  const cancelMut = useInventoryAction<BranchTransfer>('transfers', 'cancel');

  const run = React.useCallback(async (id: number, label: string, mut: typeof dispatchMut) => {
    try {
      await mut.mutateAsync({ id });
      toast.success(`Transfer ${label}.`);
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : `Failed to ${label}.`);
    }
  }, []);

  const columns: ColumnDef<BranchTransfer, unknown>[] = [
    { accessorKey: 'tr_no', header: () => t('transfer.no') },
    { accessorKey: 'from_branch', header: () => t('transfer.from') },
    { accessorKey: 'to_branch', header: () => t('transfer.to') },
    {
      accessorKey: 'status',
      header: () => t('common.status'),
      cell: ({ row }) => <StatusBadge value={row.original.status} />,
    },
    { accessorKey: 'dispatched_at', header: () => 'Dispatched' },
    { accessorKey: 'received_at', header: () => 'Received' },
    {
      id: 'actions',
      header: () => t('common.actions'),
      cell: ({ row }) => {
        if (!canTransfer) return null;
        const { id, status } = row.original;
        return (
          <div className="flex gap-1">
            {status === 'DRAFT' && (
              <Button
                size="sm"
                variant="outline"
                onClick={() => run(id, 'dispatched', dispatchMut)}
              >
                {t('transfer.dispatch')}
              </Button>
            )}
            {(status === 'IN_TRANSIT' || status === 'PART_RECEIVED') && (
              <Button size="sm" variant="outline" onClick={() => run(id, 'received', receiveMut)}>
                {t('transfer.receive')}
              </Button>
            )}
            {status === 'DRAFT' && (
              <Button size="sm" variant="outline" onClick={() => run(id, 'cancelled', cancelMut)}>
                {t('transfer.cancel')}
              </Button>
            )}
          </div>
        );
      },
    },
  ];

  return (
    <InventoryListPage<BranchTransfer>
      endpoint="transfers"
      title={t('transfers.title')}
      subtitle="Two-step transfers between branches with in-transit tracking."
      columns={columns}
    />
  );
}
