import * as React from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

const APP_NAME = import.meta.env.VITE_APP_NAME ?? 'AsliChoice Admin';

const loginSchema = z.object({
  identifier: z.string().min(3, 'Enter your phone or email'),
  password: z.string().min(1, 'Password is required'),
});

type LoginValues = z.infer<typeof loginSchema>;
type FieldErrors = Partial<Record<keyof LoginValues, string>>;

/**
 * UI-only login placeholder. Real authentication (OTP + password) is
 * wired in plan 006-authentication-skeleton.md. This page exists so the
 * shell + router are exercisable end-to-end from day one.
 */
export function LoginPage() {
  const navigate = useNavigate();
  const [errors, setErrors] = React.useState<FieldErrors>({});
  const [submitting, setSubmitting] = React.useState(false);

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const payload = {
      identifier: String(data.get('identifier') ?? ''),
      password: String(data.get('password') ?? ''),
    };
    const parsed = loginSchema.safeParse(payload);
    if (!parsed.success) {
      const next: FieldErrors = {};
      for (const issue of parsed.error.issues) {
        const key = issue.path[0] as keyof LoginValues | undefined;
        if (key && !next[key]) next[key] = issue.message;
      }
      setErrors(next);
      return;
    }
    setErrors({});
    setSubmitting(true);
    toast.info('Authentication will be wired in plan 006. Continuing as a guest.');
    window.setTimeout(() => {
      setSubmitting(false);
      navigate('/', { replace: true });
    }, 400);
  }

  return (
    <div className="grid min-h-screen place-items-center bg-muted/30 p-4">
      <div className="w-full max-w-sm rounded-lg border bg-card p-6 shadow-sm">
        <div className="mb-6 space-y-1 text-center">
          <h1 className="text-xl font-semibold tracking-tight">Sign in</h1>
          <p className="text-sm text-muted-foreground">{APP_NAME}</p>
        </div>
        <form className="space-y-4" onSubmit={handleSubmit} noValidate>
          <div className="space-y-1.5">
            <Label htmlFor="identifier">Phone or email</Label>
            <Input
              id="identifier"
              name="identifier"
              autoComplete="username"
              aria-invalid={errors.identifier ? true : undefined}
              aria-describedby={errors.identifier ? 'identifier-error' : undefined}
            />
            {errors.identifier && (
              <p id="identifier-error" className="text-xs text-destructive">
                {errors.identifier}
              </p>
            )}
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              aria-invalid={errors.password ? true : undefined}
              aria-describedby={errors.password ? 'password-error' : undefined}
            />
            {errors.password && (
              <p id="password-error" className="text-xs text-destructive">
                {errors.password}
              </p>
            )}
          </div>
          <Button type="submit" className="w-full" disabled={submitting}>
            {submitting ? 'Signing in…' : 'Sign in'}
          </Button>
        </form>
      </div>
    </div>
  );
}
