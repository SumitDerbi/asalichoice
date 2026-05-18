import { toast } from 'sonner';
import type { ColumnDef } from '@tanstack/react-table';
import { Button } from '@/components/ui/button';
import { ApiError } from '@/lib/api/errors';
import { PurchaseListPage, StatusBadge } from '../components/purchase-list-page';
import { InvoiceFromGRNsForm } from '../components/invoice-from-grns-form';
import { usePurchaseAction } from '../api/hooks';
import { useCanManageInvoices, useCanRecordPayments } from '../lib/use-permission';
import type { PurchaseInvoice } from '../api/types';
import { t } from '../lib/i18n';

const STATUS_OPTIONS = [
  { value: 'DRAFT', label: 'Draft' },
  { value: 'POSTED', label: 'Posted' },
  { value: 'PART_PAID', label: 'Part paid' },
  { value: 'PAID', label: 'Paid' },
  { value: 'CANCELLED', label: 'Cancelled' },
];

export function InvoicesPage() {
  const canManage = useCanManageInvoices();
  const canPay = useCanRecordPayments();
  const post = usePurchaseAction<PurchaseInvoice>('invoices', 'post');
  const pay = usePurchaseAction<PurchaseInvoice>('invoices', 'pay');

  const run = async (label: string, fn: () => Promise<unknown>) => {
    try {
      await fn();
      toast.success(`${label} ✓`);
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : `${label} failed`);
    }
  };

  const columns: ColumnDef<PurchaseInvoice, unknown>[] = [
    { accessorKey: 'pi_no', header: () => t('pi.no') },
    { accessorKey: 'vendor', header: () => t('po.vendor') },
    { accessorKey: 'invoice_date', header: () => t('pi.invoice_date') },
    { accessorKey: 'due_date', header: () => t('pi.due_date') },
    {
      id: 'status',
      header: () => t('common.status'),
      cell: ({ row }) => <StatusBadge value={row.original.status} />,
    },
    {
      id: 'total',
      header: () => t('pi.total'),
      cell: ({ row }) => row.original.totals_json?.grand ?? '0',
    },
    {
      id: 'actions',
      header: () => <span className="sr-only">{t('common.actions')}</span>,
      cell: ({ row }) => {
        const inv = row.original;
        return (
          <div className="flex justify-end gap-2">
            {inv.status === 'DRAFT' && (
              <Button
                size="sm"
                variant="ghost"
                disabled={!canManage}
                onClick={() => run('Post', () => post.mutateAsync({ id: inv.id }))}
              >
                {t('actions.post')}
              </Button>
            )}
            {['POSTED', 'PART_PAID'].includes(inv.status) && (
              <Button
                size="sm"
                variant="ghost"
                disabled={!canPay}
                onClick={() => {
                  const amount = window.prompt('Payment amount?');
                  if (!amount) return;
                  void run('Pay', () =>
                    pay.mutateAsync({ id: inv.id, body: { amount, payment_mode: 'CASH' } }),
                  );
                }}
              >
                {t('actions.pay')}
              </Button>
            )}
          </div>
        );
      },
    },
  ];

  return (
    <PurchaseListPage<PurchaseInvoice>
      endpoint="invoices"
      title={t('invoices.title')}
      searchField="pi_no"
      filters={[{ label: t('common.status'), param: 'status', options: STATUS_OPTIONS }]}
      columns={columns}
      canCreate={canManage}
      renderCreate={(close) => <InvoiceFromGRNsForm onClose={close} />}
    />
  );
}
