import * as React from 'react';
import { useParams, Link } from 'react-router-dom';
import { PageHeader } from '@/components/shared/page-header';
import { useSaleAction, useSaleDetail } from '../api/hooks';
import { useCanCancelSale, useCanManageSales } from '../lib/use-permission';
import { t } from '../lib/i18n';

function formatMoney(value: string | number): string {
  return Number(value).toFixed(2);
}

export function SaleDetailPage() {
  const { id } = useParams();
  const numericId = id ? Number(id) : undefined;
  const { data, isLoading, isError, error } = useSaleDetail(numericId);
  const canManage = useCanManageSales();
  const canCancel = useCanCancelSale();

  const postSale = useSaleAction('post_sale');
  const cancelSale = useSaleAction('cancel');
  const addPayment = useSaleAction('add_payment');

  const [paymentMode, setPaymentMode] = React.useState('');
  const [paymentAmount, setPaymentAmount] = React.useState('');
  const [cancelReason, setCancelReason] = React.useState('');

  if (isLoading) {
    return <p className="text-sm text-muted-foreground">Loading…</p>;
  }
  if (isError) {
    return (
      <p className="text-sm text-destructive">{(error as Error)?.message ?? t('common.error')}</p>
    );
  }
  if (!data || !numericId) return null;

  const canPost =
    canManage && (data.status === 'DRAFT' || data.status === 'HELD' || data.status === 'CONFIRMED');
  const canCancelNow =
    canCancel &&
    data.status !== 'DRAFT' &&
    data.status !== 'CANCELLED' &&
    data.status !== 'REFUNDED';

  return (
    <div className="space-y-6">
      <PageHeader
        title={t('sales.detail.title', { saleNo: data.sale_no })}
        description={`${data.origin} · ${data.status}`}
        actions={
          <div className="flex gap-2">
            <Link to="/sales" className="text-sm text-muted-foreground underline">
              Back
            </Link>
          </div>
        }
      />

      <section className="grid grid-cols-2 gap-4 text-sm md:grid-cols-4">
        <div>
          <div className="text-xs text-muted-foreground">{t('common.branch')}</div>
          <div>{data.branch}</div>
        </div>
        <div>
          <div className="text-xs text-muted-foreground">{t('common.customer')}</div>
          <div>{data.customer ?? '—'}</div>
        </div>
        <div>
          <div className="text-xs text-muted-foreground">{t('common.cashier')}</div>
          <div>{data.cashier ?? '—'}</div>
        </div>
        <div>
          <div className="text-xs text-muted-foreground">Tax mode</div>
          <div>{data.tax_mode}</div>
        </div>
      </section>

      <section>
        <h3 className="mb-2 text-sm font-semibold">Items</h3>
        <table className="w-full text-sm">
          <thead className="border-b text-xs text-muted-foreground">
            <tr>
              <th className="py-1 text-left">Product / Variant</th>
              <th className="py-1 text-right">Qty</th>
              <th className="py-1 text-right">Price</th>
              <th className="py-1 text-right">Discount</th>
              <th className="py-1 text-right">Subtotal</th>
              <th className="py-1 text-right">Total</th>
            </tr>
          </thead>
          <tbody>
            {data.items.map((i) => (
              <tr key={i.id} className="border-b last:border-0">
                <td className="py-1">{i.product ?? i.variant}</td>
                <td className="py-1 text-right">{Number(i.qty).toFixed(3)}</td>
                <td className="py-1 text-right">{formatMoney(i.sale_price)}</td>
                <td className="py-1 text-right">{formatMoney(i.discount_amount)}</td>
                <td className="py-1 text-right">{formatMoney(i.line_subtotal)}</td>
                <td className="py-1 text-right">{formatMoney(i.line_total)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="grid grid-cols-2 gap-4 text-sm md:grid-cols-4">
        <div>
          <div className="text-xs text-muted-foreground">Subtotal</div>
          <div>{formatMoney(data.subtotal)}</div>
        </div>
        <div>
          <div className="text-xs text-muted-foreground">Discount</div>
          <div>{formatMoney(data.discount_total)}</div>
        </div>
        <div>
          <div className="text-xs text-muted-foreground">Tax</div>
          <div>{formatMoney(data.tax_total)}</div>
        </div>
        <div>
          <div className="text-xs text-muted-foreground">{t('common.grand_total')}</div>
          <div className="font-semibold">{formatMoney(data.grand_total)}</div>
        </div>
      </section>

      <section>
        <h3 className="mb-2 text-sm font-semibold">Payments</h3>
        {data.payments.length === 0 ? (
          <p className="text-xs text-muted-foreground">No payments recorded.</p>
        ) : (
          <table className="w-full text-sm">
            <thead className="border-b text-xs text-muted-foreground">
              <tr>
                <th className="py-1 text-left">Mode</th>
                <th className="py-1 text-right">Amount</th>
                <th className="py-1 text-left">Status</th>
                <th className="py-1 text-left">Ref</th>
              </tr>
            </thead>
            <tbody>
              {data.payments.map((p) => (
                <tr key={p.id} className="border-b last:border-0">
                  <td className="py-1">{p.payment_mode}</td>
                  <td className="py-1 text-right">{formatMoney(p.amount)}</td>
                  <td className="py-1">{p.status}</td>
                  <td className="py-1">{p.ref_no || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      {canPost ? (
        <section className="space-y-2 rounded border p-3">
          <h4 className="text-sm font-semibold">{t('sales.add_payment')}</h4>
          <div className="flex flex-wrap items-end gap-2">
            <input
              placeholder="Payment mode ID"
              value={paymentMode}
              onChange={(e) => setPaymentMode(e.target.value.replace(/[^0-9]/g, ''))}
              className="h-9 rounded border px-2 text-sm"
            />
            <input
              placeholder="Amount"
              value={paymentAmount}
              onChange={(e) => setPaymentAmount(e.target.value.replace(/[^0-9.]/g, ''))}
              className="h-9 rounded border px-2 text-sm"
            />
            <button
              type="button"
              className="h-9 rounded border px-3 text-sm"
              disabled={!paymentMode || !paymentAmount || addPayment.isPending}
              onClick={() =>
                addPayment.mutate({
                  id: numericId,
                  body: {
                    payment_mode: Number(paymentMode),
                    amount: paymentAmount,
                  },
                })
              }
            >
              Add
            </button>
          </div>
          <div>
            <button
              type="button"
              className="rounded bg-primary px-3 py-1.5 text-sm text-primary-foreground"
              disabled={postSale.isPending}
              onClick={() => postSale.mutate({ id: numericId })}
            >
              {t('sales.post')}
            </button>
          </div>
        </section>
      ) : null}

      {canCancelNow ? (
        <section className="space-y-2 rounded border p-3">
          <h4 className="text-sm font-semibold">{t('sales.cancel')}</h4>
          <input
            placeholder="Reason"
            value={cancelReason}
            onChange={(e) => setCancelReason(e.target.value)}
            className="h-9 w-full rounded border px-2 text-sm"
          />
          <button
            type="button"
            className="rounded border border-destructive px-3 py-1.5 text-sm text-destructive"
            disabled={cancelSale.isPending}
            onClick={() => cancelSale.mutate({ id: numericId, body: { reason: cancelReason } })}
          >
            {t('sales.cancel')}
          </button>
        </section>
      ) : null}
    </div>
  );
}
