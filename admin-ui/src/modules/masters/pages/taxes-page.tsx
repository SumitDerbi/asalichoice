import type { ColumnDef } from '@tanstack/react-table';
import { Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Field } from '@/lib/forms';
import { MasterListPage } from '../components/master-list-page';
import { MasterFormBody } from '../components/master-form-body';
import { taxSchema, type TaxInput } from '../schemas';
import type { Tax, TaxComponent, TaxComponentType } from '../api/types';
import { t } from '../lib/i18n';

const columns: ColumnDef<Tax, unknown>[] = [
  { accessorKey: 'code', header: () => t('common.code') },
  { accessorKey: 'name', header: () => t('common.name') },
  {
    accessorKey: 'rate_total',
    header: () => t('taxes.field.rate_total'),
    cell: ({ row }) => `${row.original.rate_total}%`,
  },
];

const TYPE_OPTIONS: TaxComponentType[] = ['CGST', 'SGST', 'IGST', 'CESS'];

const KNOWN = ['code', 'name', 'components_json'] as const;

/**
 * Editable list of (type, rate) pairs with a live running total
 * shown above. Backend computes `rate_total` and returns it; we
 * mirror that math locally so users get instant feedback while
 * the drawer is open.
 */
function ComponentsEditor({
  value,
  onChange,
  error,
}: {
  value: TaxComponent[];
  onChange: (next: TaxComponent[]) => void;
  error?: string | null;
}) {
  const liveTotal = value.reduce((sum, c) => sum + Number(c.rate || 0), 0);

  const update = (idx: number, patch: Partial<TaxComponent>) => {
    onChange(value.map((c, i) => (i === idx ? { ...c, ...patch } : c)));
  };
  const remove = (idx: number) => onChange(value.filter((_, i) => i !== idx));
  const add = () => onChange([...value, { type: 'CGST', rate: '0' }]);

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium">{t('taxes.field.components')}</span>
        <span className="text-xs font-semibold text-foreground">
          {t('taxes.components.live_total', { value: liveTotal.toFixed(2) })}
        </span>
      </div>
      <div className="space-y-2">
        {value.map((row, idx) => (
          <div key={idx} className="grid grid-cols-[1fr_1fr_auto] items-center gap-2">
            <select
              value={row.type}
              onChange={(e) => update(idx, { type: e.target.value as TaxComponentType })}
              className="flex h-9 rounded-md border border-input bg-background px-2 text-sm"
            >
              {TYPE_OPTIONS.map((opt) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
            </select>
            <Input
              type="text"
              inputMode="decimal"
              value={row.rate}
              onChange={(e) => update(idx, { rate: e.target.value })}
            />
            <Button
              type="button"
              variant="ghost"
              size="icon"
              onClick={() => remove(idx)}
              aria-label="Remove component"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        ))}
      </div>
      <Button type="button" variant="outline" size="sm" onClick={add}>
        {t('taxes.components.add')}
      </Button>
      {error && (
        <p className="text-xs text-destructive" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}

export function TaxesPage() {
  return (
    <MasterListPage<Tax, TaxInput>
      endpoint="taxes"
      permissionDomain="tax"
      title={t('taxes.title')}
      searchField="search"
      columns={columns}
      renderForm={({ initial, onSubmit, onCancel, submitting }) => (
        <MasterFormBody<TaxInput>
          schema={taxSchema}
          defaultValues={{
            code: initial.code ?? '',
            name: initial.name ?? '',
            components_json:
              initial.components_json && initial.components_json.length > 0
                ? initial.components_json
                : [{ type: 'CGST', rate: '0' }],
          }}
          knownFields={KNOWN}
          onSubmit={onSubmit}
          onCancel={onCancel}
          submitting={submitting}
        >
          {({ form, errorMap }) => (
            <>
              <form.Field name="code">
                {(f) => <Field field={f} label={t('common.code')} formErrorMap={errorMap} />}
              </form.Field>
              <form.Field name="name">
                {(f) => <Field field={f} label={t('common.name')} formErrorMap={errorMap} />}
              </form.Field>
              <form.Field name="components_json">
                {(f) => {
                  const fieldError =
                    (errorMap as { fields?: Record<string, string> } | undefined)?.fields
                      ?.components_json ?? null;
                  return (
                    <ComponentsEditor
                      value={(f.state.value as TaxComponent[]) ?? []}
                      onChange={(next) => f.handleChange(next as never)}
                      error={fieldError}
                    />
                  );
                }}
              </form.Field>
            </>
          )}
        </MasterFormBody>
      )}
    />
  );
}
