import * as React from 'react';
import type { ColumnDef } from '@tanstack/react-table';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { ApiError } from '@/lib/api/errors';
import { InventoryListPage, StatusBadge } from '../components/inventory-list-page';
import { useInventoryAction } from '../api/hooks';
import { useCanWastage } from '../lib/use-permission';
import type { Wastage } from '../api/types';
import { t } from '../lib/i18n';

export function WastagePage() {
  const canWastage = useCanWastage();
  const postMut = useInventoryAction<Wastage>('wastage', 'post');

  const onPost = React.useCallback(
    async (id: number) => {
      try {
        await postMut.mutateAsync({ id });
        toast.success('Wastage posted.');
      } catch (err) {
        toast.error(err instanceof ApiError ? err.message : 'Failed to post.');
      }
    },
    [postMut],
  );

  const columns: ColumnDef<Wastage, unknown>[] = [
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
        row.original.status === 'DRAFT' && canWastage ? (
          <Button size="sm" variant="outline" onClick={() => onPost(row.original.id)}>
            {t('actions.post')}
          </Button>
        ) : null,
    },
  ];

  return (
    <InventoryListPage<Wastage>
      endpoint="wastage"
      title={t('wastage.title')}
      subtitle="Damage / expiry / shrinkage write-offs."
      columns={columns}
    />
  );
}
