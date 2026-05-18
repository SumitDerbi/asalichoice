import * as React from 'react';
import { toast } from 'sonner';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Form, runSubmit, useAppForm } from '@/lib/forms';
import { FieldShell } from '@/lib/forms/field';
import { ApiError } from '@/lib/api/errors';
import { usePurchaseCollectionAction, usePurchaseList } from '../api/hooks';
import { invoiceFromGRNsSchema, type InvoiceFromGRNsInput } from '../schemas';
import type { GRN, PurchaseInvoice } from '../api/types';
import { RemoteSelect } from './remote-select';
import { t } from '../lib/i18n';

interface Props {
  onClose: () => void;
}

const KNOWN = [
  'vendor',
  'branch',
  'pi_no',
  'grn_ids',
  'invoice_no_vendor',
  'invoice_date',
  'due_date',
  'payment_terms',
] as const;

export function InvoiceFromGRNsForm({ onClose }: Props) {
  const mut = usePurchaseCollectionAction<PurchaseInvoice, InvoiceFromGRNsInput>(
    'invoices',
    'from-grns',
  );
  const form = useAppForm<InvoiceFromGRNsInput>({
    schema: invoiceFromGRNsSchema as unknown as z.ZodType<
      InvoiceFromGRNsInput,
      z.ZodTypeDef,
      unknown
    >,
    defaultValues: {
      vendor: 0 as number,
      branch: 0 as number,
      pi_no: '',
      grn_ids: [] as number[],
      invoice_no_vendor: '',
      invoice_date: '',
      due_date: '',
      payment_terms: '',
    },
    async onSubmit({ value }) {
      await runSubmit(value, {
        action: async (vals) => {
          try {
            await mut.mutateAsync(vals);
            toast.success('Invoice created.');
            onClose();
          } catch (err) {
            toast.error(err instanceof ApiError ? err.message : 'Save failed.');
            throw err;
          }
        },
        successMessage: null,
        knownFields: KNOWN as unknown as string[],
      });
    },
  });

  const vendorId = form.useStore((s) => s.values.vendor);
  const { data: grns } = usePurchaseList<GRN>(
    'grns',
    { status: 'APPROVED', vendor: vendorId || undefined },
    { enabled: !!vendorId },
  );

  return (
    <Form
      onSubmit={(e) => {
        e.preventDefault();
        void form.handleSubmit();
      }}
    >
      <div className="grid grid-cols-2 gap-3">
        <form.Field name="pi_no">
          {(f) => (
            <FieldShell id="pi_no" label="PI No.">
              <Input
                value={(f.state.value ?? '') as string}
                onChange={(e) => f.handleChange(e.target.value)}
              />
            </FieldShell>
          )}
        </form.Field>
        <form.Field name="invoice_no_vendor">
          {(f) => (
            <FieldShell id="invoice_no_vendor" label="Vendor invoice #">
              <Input
                value={(f.state.value ?? '') as string}
                onChange={(e) => f.handleChange(e.target.value)}
              />
            </FieldShell>
          )}
        </form.Field>
        <form.Field name="vendor">
          {(f) => (
            <FieldShell id="vendor" label={t('po.vendor')}>
              <RemoteSelect
                endpoint="purchase/vendors"
                labelFn={(r: { code: string; name: string }) => `${r.code} — ${r.name}`}
                value={Number(f.state.value) || null}
                onChange={(v) => f.handleChange(v ?? (0 as never))}
              />
            </FieldShell>
          )}
        </form.Field>
        <form.Field name="branch">
          {(f) => (
            <FieldShell id="branch" label={t('po.branch')}>
              <RemoteSelect
                endpoint="master/branches"
                labelFn={(r: { code: string; name: string }) => `${r.code} — ${r.name}`}
                value={Number(f.state.value) || null}
                onChange={(v) => f.handleChange(v ?? (0 as never))}
              />
            </FieldShell>
          )}
        </form.Field>
        <form.Field name="invoice_date">
          {(f) => (
            <FieldShell id="invoice_date" label="Invoice date">
              <Input
                type="date"
                value={(f.state.value ?? '') as string}
                onChange={(e) => f.handleChange(e.target.value)}
              />
            </FieldShell>
          )}
        </form.Field>
        <form.Field name="due_date">
          {(f) => (
            <FieldShell id="due_date" label="Due date">
              <Input
                type="date"
                value={(f.state.value ?? '') as string}
                onChange={(e) => f.handleChange(e.target.value)}
              />
            </FieldShell>
          )}
        </form.Field>
      </div>

      <form.Field name="grn_ids">
        {(f) => {
          const ids = (f.state.value ?? []) as number[];
          const toggle = (id: number) => {
            f.handleChange(
              ids.includes(id) ? ids.filter((x) => x !== id) : ([...ids, id] as never),
            );
          };
          return (
            <div className="space-y-2 rounded border p-3">
              <strong className="text-sm">Select approved GRNs</strong>
              {!vendorId ? (
                <p className="text-xs text-muted-foreground">Pick a vendor to load GRNs.</p>
              ) : !grns?.length ? (
                <p className="text-xs text-muted-foreground">No approved GRNs for this vendor.</p>
              ) : (
                <ul className="space-y-1 text-sm">
                  {grns.map((g) => (
                    <li key={g.id}>
                      <label className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={ids.includes(g.id)}
                          onChange={() => toggle(g.id)}
                        />
                        <span className="font-mono">{g.grn_no}</span>
                        <span className="text-xs text-muted-foreground">
                          received {g.received_at ?? '—'}
                        </span>
                      </label>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          );
        }}
      </form.Field>

      <div className="flex justify-end gap-2 border-t pt-3">
        <Button type="button" variant="outline" onClick={onClose} disabled={mut.isPending}>
          {t('common.cancel')}
        </Button>
        <Button type="submit" disabled={mut.isPending}>
          {mut.isPending ? t('common.loading') : t('common.save')}
        </Button>
      </div>
    </Form>
  );
}
