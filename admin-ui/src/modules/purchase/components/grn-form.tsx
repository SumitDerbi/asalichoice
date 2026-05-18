import * as React from 'react';
import { toast } from 'sonner';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Form, runSubmit, useAppForm } from '@/lib/forms';
import { FieldShell } from '@/lib/forms/field';
import { ApiError } from '@/lib/api/errors';
import { usePurchaseCreate } from '../api/hooks';
import { grnSchema, type GRNInput } from '../schemas';
import type { GRN } from '../api/types';
import { RemoteSelect } from './remote-select';
import { t } from '../lib/i18n';

interface GRNFormProps {
  onClose: () => void;
}

const EMPTY_LINE = {
  product: null as number | null,
  qty_received: '1',
  qty_accepted: '1',
  qty_rejected: '0',
  rejection_reason: '',
  batch_no: '',
  mfg_date: '',
  expiry_date: '',
  cost_price: '0',
};

const KNOWN_FIELDS = [
  'grn_no',
  'po',
  'vendor',
  'branch',
  'received_at',
  'vehicle_no',
  'transporter',
  'items',
] as const;

export function GRNForm({ onClose }: GRNFormProps) {
  const createMut = usePurchaseCreate<GRN, GRNInput>('grns');

  const form = useAppForm<GRNInput>({
    schema: grnSchema as unknown as z.ZodType<GRNInput, z.ZodTypeDef, unknown>,
    defaultValues: {
      grn_no: '',
      po: null,
      vendor: 0 as number,
      branch: 0 as number,
      received_at: '',
      vehicle_no: '',
      transporter: '',
      items: [EMPTY_LINE as GRNInput['items'][number]],
    },
    async onSubmit({ value }) {
      await runSubmit(value, {
        action: async (vals) => {
          try {
            await createMut.mutateAsync(vals);
            toast.success('GRN created.');
            onClose();
          } catch (err) {
            toast.error(err instanceof ApiError ? err.message : 'Save failed.');
            throw err;
          }
        },
        successMessage: null,
        knownFields: KNOWN_FIELDS as unknown as string[],
      });
    },
  });

  const submitting = createMut.isPending;

  return (
    <Form
      onSubmit={(e) => {
        e.preventDefault();
        void form.handleSubmit();
      }}
    >
      <div className="grid grid-cols-2 gap-3">
        <form.Field name="grn_no">
          {(f) => (
            <FieldShell id="grn_no" label="GRN No.">
              <Input
                value={(f.state.value ?? '') as string}
                onChange={(e) => f.handleChange(e.target.value)}
              />
            </FieldShell>
          )}
        </form.Field>
        <form.Field name="received_at">
          {(f) => (
            <FieldShell id="received_at" label="Received at">
              <Input
                type="date"
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
        <form.Field name="po">
          {(f) => (
            <FieldShell id="po" label="Against PO (optional)">
              <RemoteSelect
                endpoint="purchase/pos"
                params={{ status: 'APPROVED' }}
                labelFn={(r: { po_no: string }) => r.po_no}
                value={(f.state.value as number | null) ?? null}
                onChange={(v) => f.handleChange(v as never)}
              />
            </FieldShell>
          )}
        </form.Field>
        <form.Field name="vehicle_no">
          {(f) => (
            <FieldShell id="vehicle_no" label="Vehicle">
              <Input
                value={(f.state.value ?? '') as string}
                onChange={(e) => f.handleChange(e.target.value)}
              />
            </FieldShell>
          )}
        </form.Field>
      </div>

      <form.Field name="items" mode="array">
        {(field) => {
          const rows = (field.state.value ?? []) as GRNInput['items'];
          return (
            <div className="space-y-2 rounded border p-3">
              <div className="flex items-center justify-between">
                <strong className="text-sm">Received items</strong>
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  onClick={() => field.pushValue(EMPTY_LINE as GRNInput['items'][number])}
                >
                  + Add line
                </Button>
              </div>
              <table className="w-full text-xs">
                <thead className="text-left text-muted-foreground">
                  <tr>
                    <th className="pb-1">Product</th>
                    <th className="pb-1">Batch</th>
                    <th className="pb-1">Mfg</th>
                    <th className="pb-1">Expiry</th>
                    <th className="pb-1">Rcv</th>
                    <th className="pb-1">Acc</th>
                    <th className="pb-1">Rej</th>
                    <th className="pb-1">Cost</th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {rows.map((_row, idx) => (
                    <tr key={idx} className="align-top">
                      <td className="pr-1">
                        <form.Field name={`items[${idx}].product` as never}>
                          {(f) => (
                            <RemoteSelect
                              endpoint="catalog/products"
                              labelFn={(r: { code: string; name: string }) =>
                                `${r.code} — ${r.name}`
                              }
                              value={f.state.value as number | null}
                              onChange={(v) => f.handleChange(v as never)}
                              className="w-full"
                            />
                          )}
                        </form.Field>
                      </td>
                      <td className="pr-1">
                        <form.Field name={`items[${idx}].batch_no` as never}>
                          {(f) => (
                            <Input
                              className="h-9"
                              value={(f.state.value ?? '') as string}
                              onChange={(e) => f.handleChange(e.target.value as never)}
                            />
                          )}
                        </form.Field>
                      </td>
                      <td className="pr-1">
                        <form.Field name={`items[${idx}].mfg_date` as never}>
                          {(f) => (
                            <Input
                              type="date"
                              className="h-9"
                              value={(f.state.value ?? '') as string}
                              onChange={(e) => f.handleChange(e.target.value as never)}
                            />
                          )}
                        </form.Field>
                      </td>
                      <td className="pr-1">
                        <form.Field name={`items[${idx}].expiry_date` as never}>
                          {(f) => (
                            <Input
                              type="date"
                              className="h-9"
                              value={(f.state.value ?? '') as string}
                              onChange={(e) => f.handleChange(e.target.value as never)}
                            />
                          )}
                        </form.Field>
                      </td>
                      <td className="pr-1">
                        <form.Field name={`items[${idx}].qty_received` as never}>
                          {(f) => (
                            <Input
                              className="h-9 w-16"
                              value={(f.state.value ?? '') as string}
                              onChange={(e) => f.handleChange(e.target.value as never)}
                            />
                          )}
                        </form.Field>
                      </td>
                      <td className="pr-1">
                        <form.Field name={`items[${idx}].qty_accepted` as never}>
                          {(f) => (
                            <Input
                              className="h-9 w-16"
                              value={(f.state.value ?? '') as string}
                              onChange={(e) => f.handleChange(e.target.value as never)}
                            />
                          )}
                        </form.Field>
                      </td>
                      <td className="pr-1">
                        <form.Field name={`items[${idx}].qty_rejected` as never}>
                          {(f) => (
                            <Input
                              className="h-9 w-16"
                              value={(f.state.value ?? '') as string}
                              onChange={(e) => f.handleChange(e.target.value as never)}
                            />
                          )}
                        </form.Field>
                      </td>
                      <td className="pr-1">
                        <form.Field name={`items[${idx}].cost_price` as never}>
                          {(f) => (
                            <Input
                              className="h-9 w-20"
                              value={(f.state.value ?? '') as string}
                              onChange={(e) => f.handleChange(e.target.value as never)}
                            />
                          )}
                        </form.Field>
                      </td>
                      <td className="pt-1">
                        <Button
                          type="button"
                          size="sm"
                          variant="ghost"
                          disabled={rows.length === 1}
                          onClick={() => field.removeValue(idx)}
                        >
                          ✕
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );
        }}
      </form.Field>

      <div className="flex justify-end gap-2 border-t pt-3">
        <Button type="button" variant="outline" onClick={onClose} disabled={submitting}>
          {t('common.cancel')}
        </Button>
        <Button type="submit" disabled={submitting}>
          {submitting ? t('common.loading') : t('common.save')}
        </Button>
      </div>
    </Form>
  );
}
