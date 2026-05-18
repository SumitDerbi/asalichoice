import { toast } from 'sonner';
import type { ColumnDef } from '@tanstack/react-table';
import { Button } from '@/components/ui/button';
import { ApiError } from '@/lib/api/errors';
import { PurchaseListPage, StatusBadge } from '../components/purchase-list-page';
import { GRNForm } from '../components/grn-form';
import { usePurchaseAction } from '../api/hooks';
import { useCanManageGRNs, useCanApproveGRNs } from '../lib/use-permission';
import type { GRN } from '../api/types';
import { t } from '../lib/i18n';

const STATUS_OPTIONS = [
  { value: 'DRAFT', label: 'Draft' },
  { value: 'SUBMITTED', label: 'Submitted' },
  { value: 'APPROVED', label: 'Approved' },
  { value: 'REJECTED', label: 'Rejected' },
];

export function GRNsPage() {
  const canManage = useCanManageGRNs();
  const canApprove = useCanApproveGRNs();
  const submit = usePurchaseAction<GRN>('grns', 'submit');
  const approve = usePurchaseAction<GRN>('grns', 'approve');
  const reject = usePurchaseAction<GRN>('grns', 'reject');

  const run = async (label: string, fn: () => Promise<unknown>) => {
    try {
      await fn();
      toast.success(`${label} ✓`);
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : `${label} failed`);
    }
  };

  const columns: ColumnDef<GRN, unknown>[] = [
    { accessorKey: 'grn_no', header: () => t('grn.no') },
    { accessorKey: 'po', header: () => t('grn.po') },
    { accessorKey: 'vendor', header: () => t('po.vendor') },
    { accessorKey: 'received_at', header: () => t('grn.received_at') },
    {
      id: 'status',
      header: () => t('common.status'),
      cell: ({ row }) => <StatusBadge value={row.original.status} />,
    },
    {
      id: 'actions',
      header: () => <span className="sr-only">{t('common.actions')}</span>,
      cell: ({ row }) => {
        const g = row.original;
        return (
          <div className="flex justify-end gap-2">
            {g.status === 'DRAFT' && (
              <Button
                size="sm"
                variant="ghost"
                disabled={!canManage}
                onClick={() => run('Submit', () => submit.mutateAsync({ id: g.id }))}
              >
                {t('actions.submit')}
              </Button>
            )}
            {g.status === 'SUBMITTED' && (
              <>
                <Button
                  size="sm"
                  variant="ghost"
                  disabled={!canApprove}
                  onClick={() => run('Approve', () => approve.mutateAsync({ id: g.id }))}
                >
                  {t('actions.approve')}
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  disabled={!canApprove}
                  onClick={() => {
                    const reason = window.prompt('Rejection reason?') ?? '';
                    if (!reason) return;
                    void run('Reject', () => reject.mutateAsync({ id: g.id, body: { reason } }));
                  }}
                >
                  {t('actions.reject')}
                </Button>
              </>
            )}
          </div>
        );
      },
    },
  ];

  return (
    <PurchaseListPage<GRN>
      endpoint="grns"
      title={t('grns.title')}
      searchField="grn_no"
      filters={[{ label: t('common.status'), param: 'status', options: STATUS_OPTIONS }]}
      columns={columns}
      canCreate={canManage}
      renderCreate={(close) => <GRNForm onClose={close} />}
    />
  );
}
