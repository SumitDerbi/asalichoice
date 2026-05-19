import * as React from 'react';
import type { ColumnDef } from '@tanstack/react-table';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { ApiError } from '@/lib/api/errors';
import { InventoryListPage, StatusBadge } from '../components/inventory-list-page';
import { useInventoryAction } from '../api/hooks';
import { useCanAdjust } from '../lib/use-permission';
import type { StockAdjustment } from '../api/types';
import { t } from '../lib/i18n';

export function AdjustmentsPage() {
  const canAdjust = useCanAdjust();
  const postMut = useInventoryAction<StockAdjustment>('adjustments', 'post');

  const onPost = React.useCallback(
    async (id: number) => {
      try {
        await postMut.mutateAsync({ id });
        toast.success('Adjustment posted.');
      } catch (err) {
        toast.error(err instanceof ApiError ? err.message : 'Failed to post.');
      }
    },
    [postMut],
  );

  const columns: ColumnDef<StockAdjustment, unknown>[] = [
    { accessorKey: 'doc_no', header: () => 'Doc #' },
    { accessorKey: 'branch', header: () => t('common.branch') },
    {
      accessorKey: 'status',
      header: () => t('common.status'),
      cell: ({ row }) => <StatusBadge value={row.original.status} />,
    },
    { accessorKey: 'posted_at', header: () => 'Posted at' },
    {
      id: 'actions',
      header: () => t('common.actions'),
      cell: ({ row }) =>
        row.original.status === 'DRAFT' && canAdjust ? (
          <Button size="sm" variant="outline" onClick={() => onPost(row.original.id)}>
            {t('actions.post')}
          </Button>
        ) : null,
    },
  ];

  return (
    <InventoryListPage<StockAdjustment>
      endpoint="adjustments"
      title={t('adjustments.title')}
      subtitle="Manual stock corrections with reason codes."
      columns={columns}
    />
  );
}
