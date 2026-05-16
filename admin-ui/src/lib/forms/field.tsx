import * as React from 'react';
import type { FieldApi } from '@tanstack/react-form';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { cn } from '@/lib/utils';

interface FieldShellProps {
  id: string;
  label?: React.ReactNode;
  description?: React.ReactNode;
  errorMessage?: string | null;
  className?: string;
  children: React.ReactNode;
}

/**
 * Shared label + input + description + error layout. Use directly when you
 * need a control that ``<Field>`` doesn't render (e.g. ``<Select>`` or a
 * custom widget). For plain text/email/password use ``<Field>``.
 */
export function FieldShell({
  id,
  label,
  description,
  errorMessage,
  className,
  children,
}: FieldShellProps) {
  const descriptionId = description ? `${id}-description` : undefined;
  const errorId = errorMessage ? `${id}-error` : undefined;
  return (
    <div className={cn('space-y-1.5', className)}>
      {label && <Label htmlFor={id}>{label}</Label>}
      {React.isValidElement(children)
        ? React.cloneElement(
            children as React.ReactElement<{
              id?: string;
              'aria-invalid'?: boolean;
              'aria-describedby'?: string;
            }>,
            {
              id,
              'aria-invalid': errorMessage ? true : undefined,
              'aria-describedby': [descriptionId, errorId].filter(Boolean).join(' ') || undefined,
            },
          )
        : children}
      {description && (
        <p id={descriptionId} className="text-xs text-muted-foreground">
          {description}
        </p>
      )}
      {errorMessage && (
        <p id={errorId} className="text-xs text-destructive" role="alert">
          {errorMessage}
        </p>
      )}
    </div>
  );
}

/**
 * Extract the first user-visible error from a TanStack Form field. The
 * field's ``meta.errors`` may contain raw strings (from per-field
 * validators) or objects produced by the form-level Zod validator.
 */
export function getFieldError(
  field: Pick<FieldApi<unknown, never, never, never>, 'name' | 'state'>,
  formErrorMap?: Record<string, unknown> | undefined,
): string | null {
  // Per-field errors win.
  for (const entry of field.state.meta.errors ?? []) {
    if (typeof entry === 'string' && entry) return entry;
  }
  // Form-level errors map: { fields: { email: 'Required' } }.
  const fields = (formErrorMap as { fields?: Record<string, unknown> } | undefined)?.fields;
  const candidate = fields?.[field.name as string];
  if (typeof candidate === 'string') return candidate;
  return null;
}

interface FieldProps {
  /**
   * TanStack Form field instance, typically rendered inside
   * ``form.Field`` via the ``children`` render prop.
   */
  field: FieldApi<any, any, any, any>; // eslint-disable-line @typescript-eslint/no-explicit-any
  label?: React.ReactNode;
  description?: React.ReactNode;
  /**
   * Form-level error map (``form.state.errorMap.onChange`` /
   * ``onSubmit``). When provided, ``<Field>`` will also surface
   * Zod-produced errors keyed by field name.
   */
  formErrorMap?: Record<string, unknown>;
  type?: React.HTMLInputTypeAttribute;
  placeholder?: string;
  autoComplete?: string;
  disabled?: boolean;
  className?: string;
}

/**
 * Default field component for text inputs. Renders label + ``<Input>`` +
 * description + inline error message. Wires aria-invalid /
 * aria-describedby for accessibility.
 *
 * Use ``<FieldShell>`` directly when you need a non-``<Input>`` control.
 */
export function Field({
  field,
  label,
  description,
  formErrorMap,
  type = 'text',
  placeholder,
  autoComplete,
  disabled,
  className,
}: FieldProps) {
  const error = getFieldError(field, formErrorMap);
  const id = `field-${field.name as string}`;
  return (
    <FieldShell
      id={id}
      label={label}
      description={description}
      errorMessage={error}
      className={className}
    >
      <Input
        name={field.name as string}
        type={type}
        value={(field.state.value ?? '') as string}
        onChange={(e) => field.handleChange(e.target.value as never)}
        onBlur={field.handleBlur}
        autoComplete={autoComplete}
        placeholder={placeholder}
        disabled={disabled}
      />
    </FieldShell>
  );
}
