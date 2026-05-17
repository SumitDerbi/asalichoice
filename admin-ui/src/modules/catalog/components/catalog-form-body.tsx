import * as React from 'react';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Form, runSubmit, useAppForm, mapApiErrorToFields } from '@/lib/forms';
import { t } from '../lib/i18n';

interface CatalogFormBodyProps<TValues> {
  schema: z.ZodType<TValues, z.ZodTypeDef, unknown>;
  defaultValues: TValues;
  knownFields: readonly string[];
  onSubmit: (values: TValues) => Promise<void>;
  onCancel: () => void;
  submitting: boolean;
  children: (ctx: {
    form: ReturnType<typeof useAppForm<TValues>>;
    errorMap: Record<string, unknown> | undefined;
  }) => React.ReactNode;
}

export function CatalogFormBody<TValues>(props: CatalogFormBodyProps<TValues>) {
  const { schema, defaultValues, knownFields, onSubmit, onCancel, submitting, children } = props;

  const form = useAppForm<TValues>({
    schema,
    defaultValues,
    async onSubmit({ value }) {
      await runSubmit(value, {
        action: async (vals) => {
          await onSubmit(vals);
        },
        successMessage: null,
        knownFields,
      });
    },
  });

  const errorMap = form.useStore((s) => s.errorMap);
  const errorMapForFields = pickFieldErrorMap(errorMap);

  return (
    <Form
      onSubmit={(e) => {
        e.preventDefault();
        void form.handleSubmit();
      }}
    >
      {children({ form, errorMap: errorMapForFields })}
      <div className="flex justify-end gap-2 border-t pt-3">
        <Button type="button" variant="outline" onClick={onCancel} disabled={submitting}>
          {t('common.cancel')}
        </Button>
        <Button type="submit" disabled={submitting}>
          {submitting ? t('common.loading') : t('common.save')}
        </Button>
      </div>
    </Form>
  );
}

function pickFieldErrorMap(errorMap: unknown): Record<string, unknown> | undefined {
  if (!errorMap || typeof errorMap !== 'object') return undefined;
  const map = errorMap as Record<string, unknown>;
  for (const key of ['onChange', 'onBlur', 'onSubmit'] as const) {
    const value = map[key];
    if (value && typeof value === 'object') return value as Record<string, unknown>;
  }
  return undefined;
}

export { mapApiErrorToFields };
