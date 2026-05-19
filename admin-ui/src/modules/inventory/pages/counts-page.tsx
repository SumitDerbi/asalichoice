import * as React from 'react';
import type { ColumnDef } from '@tanstack/react-table';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { ApiError } from '@/lib/api/errors';
import { InventoryListPage, StatusBadge } from '../components/inventory-list-page';
import { useInventoryAction } from '../api/hooks';
import { useCanCount } from '../lib/use-permission';
import type { PhysicalCount } from '../api/types';
import { t } from '../lib/i18n';

export function CountsPage() {
  const canCount = useCanCount();
  const markMut = useInventoryAction<PhysicalCount>('counts', 'mark-counted');
  const postMut = useInventoryAction<PhysicalCount>('counts', 'post');

  const run = React.useCallback(async (id: number, label: string, mut: typeof postMut) => {
    try {
      await mut.mutateAsync({ id });
      toast.success(`Count ${label}.`);
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : `Failed to ${label}.`);
    }
  }, []);

  const columns: ColumnDef<PhysicalCount, unknown>[] = [
    { accessorKey: 'doc_no', header: () => 'Doc #' },
    { accessorKey: 'branch', header: () => t('common.branch') },
    {
      accessorKey: 'status',
      header: () => t('common.status'),
      cell: ({ row }) => <StatusBadge value={row.original.status} />,
    },
    { accessorKey: 'counted_at', header: () => 'Counted at' },
    { accessorKey: 'posted_at', header: () => 'Posted at' },
    {
      id: 'actions',
      header: () => t('common.actions'),
      cell: ({ row }) => {
        if (!canCount) return null;
        const { id, status } = row.original;
        return (
          <div className="flex gap-1">
            {status === 'DRAFT' && (
              <Button size="sm" variant="outline" onClick={() => run(id, 'counted', markMut)}>
                {t('actions.mark_counted')}
              </Button>
            )}
            {status === 'COUNTED' && (
              <Button size="sm" variant="outline" onClick={() => run(id, 'posted', postMut)}>
                {t('actions.post')}
              </Button>
            )}
          </div>
        );
      },
    },
  ];

  return (
    <InventoryListPage<PhysicalCount>
      endpoint="counts"
      title={t('counts.title')}
      subtitle="Physical inventory counts; expected qty snapshotted on creation."
      columns={columns}
    />
  );
}
