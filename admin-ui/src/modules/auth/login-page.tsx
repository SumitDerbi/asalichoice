import * as React from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Field, Form, runSubmit, useAppForm } from '@/lib/forms';
import { useAuthStore } from '@/lib/auth/store';
import { ApiError } from '@/lib/api/errors';
import {
  loginSchema,
  otpRequestSchema,
  otpVerifySchema,
  type LoginValues,
  type OtpRequestValues,
  type OtpVerifyValues,
} from './schemas';

const APP_NAME = import.meta.env.VITE_APP_NAME ?? 'AsliChoice Admin';

function pickFieldErrorMap(errorMap: unknown): Record<string, unknown> | undefined {
  if (!errorMap || typeof errorMap !== 'object') return undefined;
  const map = errorMap as Record<string, unknown>;
  for (const key of ['onChange', 'onBlur', 'onSubmit'] as const) {
    const value = map[key];
    if (value && typeof value === 'object') return value as Record<string, unknown>;
  }
  return undefined;
}

type Mode = 'password' | 'otp';

export function LoginPage() {
  const navigate = useNavigate();
  const [mode, setMode] = React.useState<Mode>('password');

  return (
    <div className="grid min-h-screen place-items-center bg-muted/30 p-4">
      <div className="w-full max-w-sm rounded-lg border bg-card p-6 shadow-sm">
        <div className="mb-4 space-y-1 text-center">
          <h1 className="text-xl font-semibold tracking-tight">Sign in</h1>
          <p className="text-sm text-muted-foreground">{APP_NAME}</p>
        </div>

        <div className="mb-4 grid grid-cols-2 rounded-md bg-muted p-0.5 text-sm">
          <button
            type="button"
            onClick={() => setMode('password')}
            className={
              'rounded px-2 py-1 ' +
              (mode === 'password'
                ? 'bg-background font-medium shadow-sm'
                : 'text-muted-foreground')
            }
          >
            Password
          </button>
          <button
            type="button"
            onClick={() => setMode('otp')}
            className={
              'rounded px-2 py-1 ' +
              (mode === 'otp' ? 'bg-background font-medium shadow-sm' : 'text-muted-foreground')
            }
          >
            OTP
          </button>
        </div>

        {mode === 'password' ? (
          <PasswordForm onSuccess={() => navigate('/', { replace: true })} />
        ) : (
          <OtpForm onSuccess={() => navigate('/', { replace: true })} />
        )}
      </div>
    </div>
  );
}

const PASSWORD_FIELDS = ['identifier', 'password'] as const;

function PasswordForm({ onSuccess }: { onSuccess: () => void }) {
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
          knownFields: PASSWORD_FIELDS,
        });
        if (ok) onSuccess();
      } finally {
        setSubmitting(false);
      }
    },
  });

  const errorMapForFields = pickFieldErrorMap(form.useStore((s) => s.errorMap));

  return (
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
  );
}

const OTP_REQUEST_FIELDS = ['identifier'] as const;
const OTP_VERIFY_FIELDS = ['identifier', 'code'] as const;

function OtpForm({ onSuccess }: { onSuccess: () => void }) {
  const requestOTP = useAuthStore((s) => s.requestOTP);
  const loginWithOTP = useAuthStore((s) => s.loginWithOTP);
  const [step, setStep] = React.useState<'request' | 'verify'>('request');
  const [identifier, setIdentifier] = React.useState('');
  const [channelInfo, setChannelInfo] = React.useState<string | null>(null);
  const [submitting, setSubmitting] = React.useState(false);

  const requestForm = useAppForm<OtpRequestValues>({
    schema: otpRequestSchema,
    defaultValues: { identifier: '' },
    async onSubmit({ value }) {
      setSubmitting(true);
      try {
        await runSubmit(value, {
          action: async (vals) => {
            const resp = await requestOTP(vals.identifier.trim());
            setIdentifier(vals.identifier.trim());
            setChannelInfo(`Code sent via ${resp.channel}.`);
            setStep('verify');
          },
          successMessage: null,
          knownFields: OTP_REQUEST_FIELDS,
        });
      } catch (err) {
        if (err instanceof ApiError) toast.error(err.message);
      } finally {
        setSubmitting(false);
      }
    },
  });

  const verifyForm = useAppForm<OtpVerifyValues>({
    schema: otpVerifySchema,
    defaultValues: { identifier: '', code: '' },
    async onSubmit({ value }) {
      setSubmitting(true);
      try {
        const ok = await runSubmit(
          { ...value, identifier },
          {
            action: async (vals) => {
              await loginWithOTP(vals.identifier, vals.code);
            },
            successMessage: null,
            knownFields: OTP_VERIFY_FIELDS,
          },
        );
        if (ok) onSuccess();
      } finally {
        setSubmitting(false);
      }
    },
  });

  const requestErr = pickFieldErrorMap(requestForm.useStore((s) => s.errorMap));
  const verifyErr = pickFieldErrorMap(verifyForm.useStore((s) => s.errorMap));

  if (step === 'request') {
    return (
      <Form
        onSubmit={(event) => {
          event.preventDefault();
          void requestForm.handleSubmit();
        }}
      >
        <requestForm.Field name="identifier">
          {(field) => (
            <Field
              field={field}
              label="Email / mobile / employee code"
              type="text"
              autoComplete="username"
              formErrorMap={requestErr}
            />
          )}
        </requestForm.Field>
        <Button type="submit" className="w-full" disabled={submitting}>
          {submitting ? 'Sending...' : 'Send code'}
        </Button>
      </Form>
    );
  }

  return (
    <Form
      onSubmit={(event) => {
        event.preventDefault();
        void verifyForm.handleSubmit();
      }}
    >
      {channelInfo && (
        <p className="rounded border border-emerald-200 bg-emerald-50 px-2 py-1 text-xs text-emerald-700">
          {channelInfo} Sent to <strong>{identifier}</strong>.
        </p>
      )}
      <verifyForm.Field name="code">
        {(field) => (
          <Field
            field={field}
            label="Verification code"
            type="text"
            autoComplete="one-time-code"
            formErrorMap={verifyErr}
          />
        )}
      </verifyForm.Field>
      <div className="flex gap-2">
        <Button
          type="button"
          variant="outline"
          onClick={() => setStep('request')}
          disabled={submitting}
        >
          Back
        </Button>
        <Button type="submit" className="flex-1" disabled={submitting}>
          {submitting ? 'Verifying...' : 'Verify & sign in'}
        </Button>
      </div>
    </Form>
  );
}
