import * as React from 'react';
import { useForm, type FormApi, type ReactFormApi } from '@tanstack/react-form';
import type { z } from 'zod';
import { zodFormValidator } from './zod-validator';

/**
 * Thin wrapper around ``useForm`` that wires a Zod schema as the
 * form-level ``onChange`` + ``onSubmit`` validator. Returns the same
 * ``FormApi`` instance TanStack Form would normally give you.
 *
 * Usage:
 * ```tsx
 * const form = useAppForm({
 *   schema: loginSchema,
 *   defaultValues: { email: '', password: '' },
 *   onSubmit: async ({ value }) => { ... },
 * });
 * ```
 */
export interface UseAppFormOptions<TValues> {
  schema: z.ZodType<TValues, z.ZodTypeDef, unknown>;
  defaultValues: TValues;
  onSubmit: (args: {
    value: TValues;
    formApi: FormApi<TValues, undefined>;
  }) => Promise<void> | void;
}

export function useAppForm<TValues>(options: UseAppFormOptions<TValues>) {
  const validator = React.useMemo(() => zodFormValidator(options.schema), [options.schema]);
  return useForm<TValues>({
    defaultValues: options.defaultValues,
    onSubmit: options.onSubmit as never,
    validators: {
      onChange: validator as never,
      onSubmit: validator as never,
    },
  }) as ReactFormApi<TValues, undefined> & FormApi<TValues, undefined>;
}

interface FormProps extends React.FormHTMLAttributes<HTMLFormElement> {
  onSubmit?: React.FormEventHandler<HTMLFormElement>;
  children: React.ReactNode;
}

/**
 * Plain ``<form>`` with ``noValidate`` and default ``space-y-4`` spacing
 * for stacked fields. Submit wiring stays with the caller so they can
 * choose between ``form.handleSubmit()`` and a custom handler.
 */
export const Form = React.forwardRef<HTMLFormElement, FormProps>(function Form(
  { className, children, ...props },
  ref,
) {
  return (
    <form ref={ref} noValidate className={className ?? 'space-y-4'} {...props}>
      {children}
    </form>
  );
});
