import * as React from 'react';
import { toast } from 'sonner';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Form, runSubmit, useAppForm, mapApiErrorToFields } from '@/lib/forms';
import { FieldShell } from '@/lib/forms/field';
import { ApiError } from '@/lib/api/errors';
import { usePurchaseCreate } from '../api/hooks';
import { poSchema, type POInput } from '../schemas';
import type { PurchaseOrder } from '../api/types';
import { RemoteSelect } from './remote-select';
import { t } from '../lib/i18n';

interface POFormProps {
  onClose: () => void;
}

const EMPTY_LINE = {
  product: null as number | null,
  uom: 0,
  qty: '1',
  rate: '0',
  discount: '0',
};

const KNOWN_FIELDS = ['po_no', 'vendor', 'branch', 'expected_delivery', 'terms', 'items'] as const;

export function POForm({ onClose }: POFormProps) {
  const createMut = usePurchaseCreate<PurchaseOrder, POInput>('pos');

  const form = useAppForm<POInput>({
    schema: poSchema as unknown as z.ZodType<POInput, z.ZodTypeDef, unknown>,
    defaultValues: {
      po_no: '',
      vendor: 0 as number,
      branch: 0 as number,
      expected_delivery: '',
      terms: '',
      items: [EMPTY_LINE as POInput['items'][number]],
    },
    async onSubmit({ value }) {
      await runSubmit(value, {
        action: async (vals) => {
          try {
            await createMut.mutateAsync(vals);
            toast.success('Purchase order created.');
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

  const errorMap = form.useStore((s) => s.errorMap);
  const fieldErrors = pickFieldErrorMap(errorMap);
  const submitting = createMut.isPending;

  return (
    <Form
      onSubmit={(e) => {
        e.preventDefault();
        void form.handleSubmit();
      }}
    >
      <div className="grid grid-cols-2 gap-3">
        <form.Field name="po_no">
          {(f) => (
            <FieldShell id="po_no" label={t('po.no')} errorMessage={fieldErrorMsg(f, fieldErrors)}>
              <Input
                value={(f.state.value ?? '') as string}
                onChange={(e) => f.handleChange(e.target.value)}
                onBlur={f.handleBlur}
              />
            </FieldShell>
          )}
        </form.Field>
        <form.Field name="expected_delivery">
          {(f) => (
            <FieldShell id="expected_delivery" label="Expected delivery">
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
            <FieldShell
              id="vendor"
              label={t('po.vendor')}
              errorMessage={fieldErrorMsg(f, fieldErrors)}
            >
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
            <FieldShell
              id="branch"
              label={t('po.branch')}
              errorMessage={fieldErrorMsg(f, fieldErrors)}
            >
              <RemoteSelect
                endpoint="master/branches"
                labelFn={(r: { code: string; name: string }) => `${r.code} — ${r.name}`}
                value={Number(f.state.value) || null}
                onChange={(v) => f.handleChange(v ?? (0 as never))}
              />
            </FieldShell>
          )}
        </form.Field>
      </div>

      <form.Field name="items" mode="array">
        {(field) => {
          const rows = (field.state.value ?? []) as POInput['items'];
          const grand = rows.reduce((s, r) => {
            const q = Number(r.qty || '0');
            const rate = Number(r.rate || '0');
            const disc = Number(r.discount || '0');
            return s + q * rate - disc;
          }, 0);
          return (
            <div className="space-y-2 rounded border p-3">
              <div className="flex items-center justify-between">
                <strong className="text-sm">Line items</strong>
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  onClick={() => field.pushValue(EMPTY_LINE as POInput['items'][number])}
                >
                  + Add line
                </Button>
              </div>
              <table className="w-full text-xs">
                <thead className="text-left text-muted-foreground">
                  <tr>
                    <th className="pb-1">Product</th>
                    <th className="pb-1">UoM</th>
                    <th className="pb-1">Qty</th>
                    <th className="pb-1">Rate</th>
                    <th className="pb-1">Discount</th>
                    <th className="pb-1 text-right">Line total</th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row, idx) => {
                    const lineTotal =
                      Number(row.qty || '0') * Number(row.rate || '0') -
                      Number(row.discount || '0');
                    return (
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
                          <form.Field name={`items[${idx}].uom` as never}>
                            {(f) => (
                              <RemoteSelect
                                endpoint="master/uom"
                                labelFn={(r: { code: string }) => r.code}
                                value={Number(f.state.value) || null}
                                onChange={(v) => f.handleChange((v ?? 0) as never)}
                                className="w-full"
                              />
                            )}
                          </form.Field>
                        </td>
                        <td className="pr-1">
                          <form.Field name={`items[${idx}].qty` as never}>
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
                          <form.Field name={`items[${idx}].rate` as never}>
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
                          <form.Field name={`items[${idx}].discount` as never}>
                            {(f) => (
                              <Input
                                className="h-9"
                                value={(f.state.value ?? '') as string}
                                onChange={(e) => f.handleChange(e.target.value as never)}
                              />
                            )}
                          </form.Field>
                        </td>
                        <td className="pr-1 pt-2 text-right tabular-nums">
                          {lineTotal.toFixed(2)}
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
                    );
                  })}
                </tbody>
                <tfoot>
                  <tr>
                    <td colSpan={5} className="pt-2 text-right font-medium">
                      Grand total
                    </td>
                    <td className="pt-2 text-right font-medium tabular-nums">{grand.toFixed(2)}</td>
                    <td />
                  </tr>
                </tfoot>
              </table>
            </div>
          );
        }}
      </form.Field>

      <form.Field name="terms">
        {(f) => (
          <FieldShell id="terms" label="Terms">
            <Input
              value={(f.state.value ?? '') as string}
              onChange={(e) => f.handleChange(e.target.value)}
            />
          </FieldShell>
        )}
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

// Helpers (kept local to keep the file self-contained) -----------------------

function pickFieldErrorMap(errorMap: unknown): Record<string, unknown> | undefined {
  if (!errorMap || typeof errorMap !== 'object') return undefined;
  const map = errorMap as Record<string, unknown>;
  for (const key of ['onChange', 'onBlur', 'onSubmit'] as const) {
    const v = map[key];
    if (v && typeof v === 'object') return v as Record<string, unknown>;
  }
  return undefined;
}

function fieldErrorMsg(
  field: { name: unknown; state: { meta: { errors: unknown[] } } },
  errorMap: Record<string, unknown> | undefined,
): string | null {
  for (const e of field.state.meta.errors ?? []) {
    if (typeof e === 'string' && e) return e;
  }
  const fields = (errorMap as { fields?: Record<string, unknown> } | undefined)?.fields;
  const candidate = fields?.[String(field.name)];
  return typeof candidate === 'string' ? candidate : null;
}

export { mapApiErrorToFields };
