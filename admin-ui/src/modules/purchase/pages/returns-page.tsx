import { toast } from 'sonner';
import type { ColumnDef } from '@tanstack/react-table';
import { Button } from '@/components/ui/button';
import { ApiError } from '@/lib/api/errors';
import { PurchaseListPage, StatusBadge } from '../components/purchase-list-page';
import { usePurchaseAction } from '../api/hooks';
import { useHasPurchasePermission } from '../lib/use-permission';
import type { PurchaseReturn } from '../api/types';
import { t } from '../lib/i18n';

const STATUS_OPTIONS = [
  { value: 'DRAFT', label: 'Draft' },
  { value: 'POSTED', label: 'Posted' },
  { value: 'CANCELLED', label: 'Cancelled' },
];

export function ReturnsPage() {
  const canManage = useHasPurchasePermission('purchase.return.manage');
  const postMut = usePurchaseAction<PurchaseReturn>('returns', 'post');

  const run = async (label: string, fn: () => Promise<unknown>) => {
    try {
      await fn();
      toast.success(`${label} ✓`);
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : `${label} failed`);
    }
  };

  const columns: ColumnDef<PurchaseReturn, unknown>[] = [
    { accessorKey: 'pr_no', header: () => t('pr.no') },
    { accessorKey: 'grn', header: () => t('grn.no') },
    { accessorKey: 'vendor', header: () => t('po.vendor') },
    { accessorKey: 'reason', header: () => t('pr.reason') },
    {
      id: 'status',
      header: () => t('common.status'),
      cell: ({ row }) => <StatusBadge value={row.original.status} />,
    },
    {
      id: 'actions',
      header: () => <span className="sr-only">{t('common.actions')}</span>,
      cell: ({ row }) => {
        const r = row.original;
        if (r.status !== 'DRAFT') return null;
        return (
          <div className="flex justify-end">
            <Button
              size="sm"
              variant="ghost"
              disabled={!canManage}
              onClick={() => run('Post', () => postMut.mutateAsync({ id: r.id }))}
            >
              {t('actions.post')}
            </Button>
          </div>
        );
      },
    },
  ];

  return (
    <PurchaseListPage<PurchaseReturn>
      endpoint="returns"
      title={t('returns.title')}
      searchField="pr_no"
      filters={[{ label: t('common.status'), param: 'status', options: STATUS_OPTIONS }]}
      columns={columns}
    />
  );
}
