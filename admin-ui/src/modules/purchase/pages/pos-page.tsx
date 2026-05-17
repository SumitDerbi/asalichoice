import { toast } from 'sonner';
import type { ColumnDef } from '@tanstack/react-table';
import { Button } from '@/components/ui/button';
import { ApiError } from '@/lib/api/errors';
import { PurchaseListPage, StatusBadge } from '../components/purchase-list-page';
import { usePurchaseAction } from '../api/hooks';
import { useCanManagePOs, useCanApprovePOs } from '../lib/use-permission';
import type { PurchaseOrder } from '../api/types';
import { t } from '../lib/i18n';

const STATUS_OPTIONS = [
  { value: 'DRAFT', label: 'Draft' },
  { value: 'PENDING_APPROVAL', label: 'Pending approval' },
  { value: 'APPROVED', label: 'Approved' },
  { value: 'PARTIAL', label: 'Partial' },
  { value: 'RECEIVED', label: 'Received' },
  { value: 'CLOSED', label: 'Closed' },
  { value: 'CANCELLED', label: 'Cancelled' },
];

export function POsPage() {
  const canManage = useCanManagePOs();
  const canApprove = useCanApprovePOs();
  const submit = usePurchaseAction<PurchaseOrder>('pos', 'submit');
  const approve = usePurchaseAction<PurchaseOrder>('pos', 'approve');
  const cancel = usePurchaseAction<PurchaseOrder>('pos', 'cancel');

  const run = async (label: string, fn: () => Promise<unknown>) => {
    try {
      await fn();
      toast.success(`${label} ✓`);
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : `${label} failed`);
    }
  };

  const columns: ColumnDef<PurchaseOrder, unknown>[] = [
    { accessorKey: 'po_no', header: () => t('po.no') },
    { accessorKey: 'vendor', header: () => t('po.vendor') },
    { accessorKey: 'branch', header: () => t('po.branch') },
    {
      id: 'status',
      header: () => t('common.status'),
      cell: ({ row }) => <StatusBadge value={row.original.status} />,
    },
    {
      id: 'total',
      header: () => t('po.total'),
      cell: ({ row }) => row.original.totals_json?.grand ?? '0',
    },
    {
      id: 'actions',
      header: () => <span className="sr-only">{t('common.actions')}</span>,
      cell: ({ row }) => {
        const po = row.original;
        return (
          <div className="flex justify-end gap-2">
            {po.status === 'DRAFT' && (
              <Button
                size="sm"
                variant="ghost"
                disabled={!canManage}
                onClick={() => run('Submit', () => submit.mutateAsync({ id: po.id }))}
              >
                {t('actions.submit')}
              </Button>
            )}
            {po.status === 'PENDING_APPROVAL' && (
              <Button
                size="sm"
                variant="ghost"
                disabled={!canApprove}
                onClick={() => run('Approve', () => approve.mutateAsync({ id: po.id }))}
              >
                {t('actions.approve')}
              </Button>
            )}
            {['DRAFT', 'PENDING_APPROVAL', 'APPROVED'].includes(po.status) && (
              <Button
                size="sm"
                variant="ghost"
                disabled={!canManage}
                onClick={() => run('Cancel', () => cancel.mutateAsync({ id: po.id }))}
              >
                {t('actions.cancel')}
              </Button>
            )}
          </div>
        );
      },
    },
  ];

  return (
    <PurchaseListPage<PurchaseOrder>
      endpoint="pos"
      title={t('pos.title')}
      searchField="po_no"
      filters={[{ label: t('common.status'), param: 'status', options: STATUS_OPTIONS }]}
      columns={columns}
    />
  );
}
