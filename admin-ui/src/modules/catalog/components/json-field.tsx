import * as React from 'react';
import type { FieldApi } from '@tanstack/react-form';
import { FieldShell, getFieldError } from '@/lib/forms';

interface JsonFieldProps {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  field: FieldApi<any, any, any, any>;
  label: React.ReactNode;
  rows?: number;
  placeholder?: string;
  formErrorMap?: Record<string, unknown>;
}

/**
 * Textarea adapter that round-trips a JSON value through `JSON.stringify` /
 * `JSON.parse`. Displays parse errors inline. The underlying form value is
 * the parsed JS value (object / array / null).
 */
export function JsonField({ field, label, rows = 3, placeholder, formErrorMap }: JsonFieldProps) {
  const initial = React.useMemo(() => {
    const v = field.state.value;
    if (v == null || v === '') return '';
    if (typeof v === 'string') return v;
    try {
      return JSON.stringify(v, null, 2);
    } catch {
      return '';
    }
  }, [field.state.value]);
  const [text, setText] = React.useState(initial);
  const [parseError, setParseError] = React.useState<string | null>(null);
  const externalError = getFieldError(field, formErrorMap);
  const id = `field-${field.name as string}`;

  function commit(raw: string) {
    setText(raw);
    if (raw.trim() === '') {
      setParseError(null);
      field.handleChange(null as never);
      return;
    }
    try {
      const parsed = JSON.parse(raw);
      setParseError(null);
      field.handleChange(parsed as never);
    } catch (err) {
      setParseError((err as Error).message);
    }
  }

  return (
    <FieldShell id={id} label={label} errorMessage={parseError ?? externalError}>
      <textarea
        id={id}
        name={field.name as string}
        value={text}
        onChange={(e) => commit(e.target.value)}
        onBlur={field.handleBlur}
        rows={rows}
        placeholder={placeholder}
        className="flex min-h-[60px] w-full rounded-md border border-input bg-background px-3 py-2 font-mono text-xs shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
      />
    </FieldShell>
  );
}

interface CheckboxFieldProps {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  field: FieldApi<any, any, any, any>;
  label: React.ReactNode;
  formErrorMap?: Record<string, unknown>;
}

export function CheckboxField({ field, label, formErrorMap }: CheckboxFieldProps) {
  const error = getFieldError(field, formErrorMap);
  const id = `field-${field.name as string}`;
  return (
    <FieldShell id={id} label={undefined} errorMessage={error}>
      <label htmlFor={id} className="flex items-center gap-2 text-sm">
        <input
          id={id}
          name={field.name as string}
          type="checkbox"
          checked={Boolean(field.state.value)}
          onChange={(e) => field.handleChange(e.target.checked as never)}
          onBlur={field.handleBlur}
          className="h-4 w-4 rounded border-input"
        />
        <span>{label}</span>
      </label>
    </FieldShell>
  );
}
