import * as React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Field, Form, runSubmit, useAppForm } from '@/lib/forms';
import { useAuthStore } from '@/lib/auth/store';
import { loginSchema, type LoginValues } from './schemas';

const APP_NAME = import.meta.env.VITE_APP_NAME ?? 'AsliChoice Admin';
const KNOWN_FIELDS = ['identifier', 'password'] as const;

function pickFieldErrorMap(errorMap: unknown): Record<string, unknown> | undefined {
  if (!errorMap || typeof errorMap !== 'object') return undefined;
  const map = errorMap as Record<string, unknown>;
  for (const key of ['onChange', 'onBlur', 'onSubmit'] as const) {
    const value = map[key];
    if (value && typeof value === 'object') return value as Record<string, unknown>;
  }
  return undefined;
}

/**
 * Email + password sign-in. Posts to ``/api/v1/auth/login/`` via the auth
 * store, persists tokens, then routes to the dashboard. Uses the unified
 * ``<Form>`` + ``<Field>`` pattern from ``lib/forms``.
 */
export function LoginPage() {
  const navigate = useNavigate();
  const login = useAuthStore((s) => s.login);
  const [submitting, setSubmitting] = React.useState(false);

  const form = useAppForm<LoginValues>({
    schema: loginSchema,
    defaultValues: { identifier: '', password: '' },
    async onSubmit({ value }) {
      setSubmitting(true);
      try {
        const ok = await runSubmit(value, {
          action: async (vals) => {
            await login(vals.identifier.trim(), vals.password);
          },
          successMessage: null,
          knownFields: KNOWN_FIELDS,
        });
        if (ok) navigate('/', { replace: true });
      } finally {
        setSubmitting(false);
      }
    },
  });

  const errorMap = form.useStore((s) => s.errorMap);
  const errorMapForFields = pickFieldErrorMap(errorMap);

  return (
    <div className="grid min-h-screen place-items-center bg-muted/30 p-4">
      <div className="w-full max-w-sm rounded-lg border bg-card p-6 shadow-sm">
        <div className="mb-6 space-y-1 text-center">
          <h1 className="text-xl font-semibold tracking-tight">Sign in</h1>
          <p className="text-sm text-muted-foreground">{APP_NAME}</p>
        </div>
        <Form
          onSubmit={(event) => {
            event.preventDefault();
            void form.handleSubmit();
          }}
        >
          <form.Field name="identifier">
            {(field) => (
              <Field
                field={field}
                label="Email / mobile / employee code"
                type="text"
                autoComplete="username"
                formErrorMap={errorMapForFields}
              />
            )}
          </form.Field>
          <form.Field name="password">
            {(field) => (
              <Field
                field={field}
                label="Password"
                type="password"
                autoComplete="current-password"
                formErrorMap={errorMapForFields}
              />
            )}
          </form.Field>
          <Button type="submit" className="w-full" disabled={submitting}>
            {submitting ? 'Signing in...' : 'Sign in'}
          </Button>
        </Form>
      </div>
    </div>
  );
}
