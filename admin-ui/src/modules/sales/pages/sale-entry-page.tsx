import * as React from 'react';
import { useNavigate } from 'react-router-dom';
import { PageHeader } from '@/components/shared/page-header';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useCreateSale } from '../api/hooks';
import { useCanCreateB2B, useCanManageSales } from '../lib/use-permission';
import type { SaleOrigin } from '../api/types';
import { t } from '../lib/i18n';

interface DraftItem {
  product: string;
  variant: string;
  uom: string;
  qty: string;
  sale_price: string;
  discount_amount: string;
  tax: string;
}

interface DraftPayment {
  payment_mode: string;
  amount: string;
}

const EMPTY_ITEM: DraftItem = {
  product: '',
  variant: '',
  uom: '',
  qty: '1',
  sale_price: '0',
  discount_amount: '0',
  tax: '',
};

const EMPTY_PAYMENT: DraftPayment = { payment_mode: '', amount: '' };

interface SaleEntryPageProps {
  origin?: SaleOrigin;
}

export function SaleEntryPage({ origin = 'POS' }: SaleEntryPageProps) {
  const navigate = useNavigate();
  const canManage = useCanManageSales();
  const canB2B = useCanCreateB2B();

  const [branch, setBranch] = React.useState('');
  const [customer, setCustomer] = React.useState('');
  const [taxMode, setTaxMode] = React.useState<'INCLUSIVE' | 'EXCLUSIVE'>('EXCLUSIVE');
  const [items, setItems] = React.useState<DraftItem[]>([{ ...EMPTY_ITEM }]);
  const [payments, setPayments] = React.useState<DraftPayment[]>([{ ...EMPTY_PAYMENT }]);
  const [autoPost, setAutoPost] = React.useState(false);

  const createSale = useCreateSale();

  const isB2B = origin === 'B2B';
  const allowed = isB2B ? canB2B : canManage;

  if (!allowed) {
    return (
      <div className="space-y-2">
        <PageHeader
          title={isB2B ? t('sales.b2b') : t('sales.new')}
          description="You don't have permission to create sales."
        />
      </div>
    );
  }

  function updateItem(idx: number, patch: Partial<DraftItem>) {
    setItems((prev) => prev.map((it, i) => (i === idx ? { ...it, ...patch } : it)));
  }

  function updatePayment(idx: number, patch: Partial<DraftPayment>) {
    setPayments((prev) => prev.map((p, i) => (i === idx ? { ...p, ...patch } : p)));
  }

  function handleSubmit() {
    const body: Record<string, unknown> = {
      origin,
      branch: Number(branch),
      customer: customer ? Number(customer) : null,
      tax_mode: taxMode,
      auto_post: autoPost,
      items: items
        .filter((it) => it.qty && (it.product || it.variant))
        .map((it) => ({
          product: it.product ? Number(it.product) : null,
          variant: it.variant ? Number(it.variant) : null,
          uom: Number(it.uom),
          qty: it.qty,
          sale_price: it.sale_price,
          discount_amount: it.discount_amount || '0',
          ...(it.tax ? { tax: Number(it.tax) } : {}),
        })),
      payments: payments
        .filter((p) => p.payment_mode && p.amount)
        .map((p) => ({
          payment_mode: Number(p.payment_mode),
          amount: p.amount,
        })),
    };

    createSale.mutate(body, {
      onSuccess: (sale) => navigate(`/sales/${sale.id}`),
    });
  }

  return (
    <div className="space-y-4">
      <PageHeader
        title={isB2B ? t('sales.b2b') : t('sales.new')}
        description="Create a draft sale; optionally auto-post."
      />
      <section className="grid grid-cols-1 gap-3 md:grid-cols-4">
        <div className="space-y-1">
          <Label className="text-xs" htmlFor="entry-branch">
            Branch ID
          </Label>
          <Input
            id="entry-branch"
            value={branch}
            onChange={(e) => setBranch(e.target.value.replace(/[^0-9]/g, ''))}
            className="h-9"
          />
        </div>
        <div className="space-y-1">
          <Label className="text-xs" htmlFor="entry-customer">
            Customer ID
          </Label>
          <Input
            id="entry-customer"
            value={customer}
            onChange={(e) => setCustomer(e.target.value.replace(/[^0-9]/g, ''))}
            className="h-9"
          />
        </div>
        <div className="space-y-1">
          <Label className="text-xs" htmlFor="entry-tax-mode">
            Tax mode
          </Label>
          <select
            id="entry-tax-mode"
            value={taxMode}
            onChange={(e) => setTaxMode(e.target.value as 'INCLUSIVE' | 'EXCLUSIVE')}
            className="h-9 rounded border px-2 text-sm"
          >
            <option value="EXCLUSIVE">EXCLUSIVE</option>
            <option value="INCLUSIVE">INCLUSIVE</option>
          </select>
        </div>
        <div className="flex items-end">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={autoPost}
              onChange={(e) => setAutoPost(e.target.checked)}
            />
            Auto-post
          </label>
        </div>
      </section>

      <section className="space-y-2">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold">Items</h3>
          <button
            type="button"
            className="text-xs text-primary underline"
            onClick={() => setItems((prev) => [...prev, { ...EMPTY_ITEM }])}
          >
            + Add item
          </button>
        </div>
        <table className="w-full text-sm">
          <thead className="border-b text-xs text-muted-foreground">
            <tr>
              <th className="py-1 text-left">Product ID</th>
              <th className="py-1 text-left">Variant ID</th>
              <th className="py-1 text-left">UoM ID</th>
              <th className="py-1 text-right">Qty</th>
              <th className="py-1 text-right">Price</th>
              <th className="py-1 text-right">Discount</th>
              <th className="py-1 text-left">Tax ID</th>
            </tr>
          </thead>
          <tbody>
            {items.map((it, idx) => (
              <tr key={idx} className="border-b last:border-0">
                <td className="py-1">
                  <Input
                    className="h-8"
                    value={it.product}
                    onChange={(e) =>
                      updateItem(idx, { product: e.target.value.replace(/[^0-9]/g, '') })
                    }
                  />
                </td>
                <td className="py-1">
                  <Input
                    className="h-8"
                    value={it.variant}
                    onChange={(e) =>
                      updateItem(idx, { variant: e.target.value.replace(/[^0-9]/g, '') })
                    }
                  />
                </td>
                <td className="py-1">
                  <Input
                    className="h-8"
                    value={it.uom}
                    onChange={(e) =>
                      updateItem(idx, { uom: e.target.value.replace(/[^0-9]/g, '') })
                    }
                  />
                </td>
                <td className="py-1">
                  <Input
                    className="h-8 text-right"
                    value={it.qty}
                    onChange={(e) => updateItem(idx, { qty: e.target.value })}
                  />
                </td>
                <td className="py-1">
                  <Input
                    className="h-8 text-right"
                    value={it.sale_price}
                    onChange={(e) => updateItem(idx, { sale_price: e.target.value })}
                  />
                </td>
                <td className="py-1">
                  <Input
                    className="h-8 text-right"
                    value={it.discount_amount}
                    onChange={(e) => updateItem(idx, { discount_amount: e.target.value })}
                  />
                </td>
                <td className="py-1">
                  <Input
                    className="h-8"
                    value={it.tax}
                    onChange={(e) =>
                      updateItem(idx, { tax: e.target.value.replace(/[^0-9]/g, '') })
                    }
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="space-y-2">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold">Payments</h3>
          <button
            type="button"
            className="text-xs text-primary underline"
            onClick={() => setPayments((prev) => [...prev, { ...EMPTY_PAYMENT }])}
          >
            + Add payment
          </button>
        </div>
        <table className="w-full text-sm">
          <thead className="border-b text-xs text-muted-foreground">
            <tr>
              <th className="py-1 text-left">Mode ID</th>
              <th className="py-1 text-right">Amount</th>
            </tr>
          </thead>
          <tbody>
            {payments.map((p, idx) => (
              <tr key={idx} className="border-b last:border-0">
                <td className="py-1">
                  <Input
                    className="h-8"
                    value={p.payment_mode}
                    onChange={(e) =>
                      updatePayment(idx, { payment_mode: e.target.value.replace(/[^0-9]/g, '') })
                    }
                  />
                </td>
                <td className="py-1">
                  <Input
                    className="h-8 text-right"
                    value={p.amount}
                    onChange={(e) => updatePayment(idx, { amount: e.target.value })}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {createSale.isError ? (
        <p className="text-sm text-destructive">{(createSale.error as Error)?.message}</p>
      ) : null}

      <div className="flex justify-end">
        <button
          type="button"
          disabled={!branch || createSale.isPending}
          onClick={handleSubmit}
          className="rounded bg-primary px-3 py-1.5 text-sm text-primary-foreground disabled:opacity-50"
        >
          {createSale.isPending ? 'Saving…' : 'Save sale'}
        </button>
      </div>
    </div>
  );
}
