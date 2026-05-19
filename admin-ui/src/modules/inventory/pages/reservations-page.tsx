import * as React from 'react';
import type { ColumnDef } from '@tanstack/react-table';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { ApiError } from '@/lib/api/errors';
import { InventoryListPage, StatusBadge } from '../components/inventory-list-page';
import { useInventoryAction } from '../api/hooks';
import { useCanManageReservations } from '../lib/use-permission';
import type { Reservation } from '../api/types';
import { t } from '../lib/i18n';

export function ReservationsPage() {
  const canManage = useCanManageReservations();
  const releaseMut = useInventoryAction<Reservation>('reservations', 'release');
  const consumeMut = useInventoryAction<Reservation>('reservations', 'consume');

  const handle = React.useCallback(
    async (id: number, action: 'release' | 'consume') => {
      const mut = action === 'release' ? releaseMut : consumeMut;
      try {
        await mut.mutateAsync({ id });
        toast.success(`Reservation ${action}d.`);
      } catch (err) {
        toast.error(err instanceof ApiError ? err.message : `Failed to ${action}.`);
      }
    },
    [releaseMut, consumeMut],
  );

  const columns: ColumnDef<Reservation, unknown>[] = [
    { accessorKey: 'id', header: () => 'ID' },
    { accessorKey: 'product', header: () => t('common.product') },
    { accessorKey: 'branch', header: () => t('common.branch') },
    { accessorKey: 'qty', header: () => t('common.qty') },
    { accessorKey: 'ref_type', header: () => 'Ref. type' },
    { accessorKey: 'ref_id', header: () => 'Ref. id' },
    {
      accessorKey: 'status',
      header: () => t('common.status'),
      cell: ({ row }) => <StatusBadge value={row.original.status} />,
    },
    {
      id: 'actions',
      header: () => t('common.actions'),
      cell: ({ row }) =>
        row.original.status === 'ACTIVE' && canManage ? (
          <div className="flex gap-1">
            <Button size="sm" variant="outline" onClick={() => handle(row.original.id, 'release')}>
              {t('actions.release')}
            </Button>
            <Button size="sm" variant="outline" onClick={() => handle(row.original.id, 'consume')}>
              {t('actions.consume')}
            </Button>
          </div>
        ) : null,
    },
  ];

  return (
    <InventoryListPage<Reservation>
      endpoint="reservations"
      title={t('reservations.title')}
      subtitle="Soft-blocks held against sales orders or manual holds."
      columns={columns}
    />
  );
}
