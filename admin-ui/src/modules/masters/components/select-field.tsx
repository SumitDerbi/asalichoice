import * as React from 'react';
import type { FieldApi } from '@tanstack/react-form';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { FieldShell, getFieldError } from '@/lib/forms';
import { useMasterList } from '../api/hooks';
import type { MasterEndpoint } from '../api/hooks';

/**
 * Lightweight `<select>` adapter for TanStack Form. Use for FK pickers
 * (country → state → city, parent links, branch select, etc.).
 */
interface SelectFieldProps<T> {
  field: FieldApi<any, any, any, any>; // eslint-disable-line @typescript-eslint/no-explicit-any
  label: React.ReactNode;
  options: Array<{ value: T; label: string }>;
  placeholder?: string;
  allowEmpty?: boolean;
  emptyLabel?: string;
  formErrorMap?: Record<string, unknown>;
}

export function SelectField<T extends string | number>({
  field,
  label,
  options,
  placeholder,
  allowEmpty,
  emptyLabel,
  formErrorMap,
}: SelectFieldProps<T>) {
  const error = getFieldError(field, formErrorMap);
  const id = `field-${field.name as string}`;
  const value = field.state.value;
  // When the select is non-clearable (no empty option) and the current form
  // value matches none of the rendered options, the browser visually selects
  // the first option but the form state stays at its initial (often 0 / null)
  // value — which then fails "required" validation even though the user can
  // see a value. Sync the form state to the first option to match what is
  // actually shown.
  React.useEffect(() => {
    if (allowEmpty) return;
    if (options.length === 0) return;
    const currentMatches = options.some((o) => String(o.value) === String(value ?? ''));
    if (!currentMatches) {
      field.handleChange(options[0].value as never);
    }
  }, [allowEmpty, options, value, field]);
  return (
    <FieldShell id={id} label={label} errorMessage={error}>
      <select
        id={id}
        name={field.name as string}
        value={value == null ? '' : String(value)}
        onChange={(e) => {
          const raw = e.target.value;
          if (raw === '') {
            field.handleChange(null as never);
            return;
          }
          // Coerce to number when options are numeric
          const numericOpt = options.find((o) => String(o.value) === raw);
          field.handleChange((numericOpt?.value ?? raw) as never);
        }}
        onBlur={field.handleBlur}
        className="flex h-9 w-full rounded-md border border-input bg-background px-3 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
      >
        {allowEmpty && <option value="">{emptyLabel ?? placeholder ?? '—'}</option>}
        {options.map((opt) => (
          <option key={String(opt.value)} value={String(opt.value)}>
            {opt.label}
          </option>
        ))}
      </select>
    </FieldShell>
  );
}

/**
 * Async select that loads its options from a master endpoint.
 * Reuses TanStack Query cache so multiple pickers share data.
 */
interface RemoteSelectFieldProps {
  field: FieldApi<any, any, any, any>; // eslint-disable-line @typescript-eslint/no-explicit-any
  label: React.ReactNode;
  endpoint: MasterEndpoint;
  /** How to derive a display label from a row. */
  getLabel: (row: any) => string; // eslint-disable-line @typescript-eslint/no-explicit-any
  /** Param filter (e.g. `{ country: 1 }` for cascading State select). */
  params?: Record<string, string | number | undefined>;
  allowEmpty?: boolean;
  formErrorMap?: Record<string, unknown>;
}

export function RemoteSelectField({
  field,
  label,
  endpoint,
  getLabel,
  params,
  allowEmpty = true,
  formErrorMap,
}: RemoteSelectFieldProps) {
  const { data, isLoading } = useMasterList<{ id: number; is_active: boolean }>(endpoint, params);
  const options = React.useMemo(
    () => (data ?? []).map((row) => ({ value: row.id, label: getLabel(row) })),
    [data, getLabel],
  );
  if (isLoading) {
    return (
      <div className="space-y-1.5">
        <Label>{label}</Label>
        <Input disabled placeholder="Loading…" />
      </div>
    );
  }
  return (
    <SelectField
      field={field}
      label={label}
      options={options}
      allowEmpty={allowEmpty}
      emptyLabel="—"
      formErrorMap={formErrorMap}
    />
  );
}

/** Plain textarea field. */
interface TextareaFieldProps {
  field: FieldApi<any, any, any, any>; // eslint-disable-line @typescript-eslint/no-explicit-any
  label: React.ReactNode;
  rows?: number;
  formErrorMap?: Record<string, unknown>;
}

export function TextareaField({ field, label, rows = 3, formErrorMap }: TextareaFieldProps) {
  const error = getFieldError(field, formErrorMap);
  const id = `field-${field.name as string}`;
  return (
    <FieldShell id={id} label={label} errorMessage={error}>
      <textarea
        id={id}
        name={field.name as string}
        value={(field.state.value ?? '') as string}
        onChange={(e) => field.handleChange(e.target.value as never)}
        onBlur={field.handleBlur}
        rows={rows}
        className="flex min-h-[60px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
      />
    </FieldShell>
  );
}
