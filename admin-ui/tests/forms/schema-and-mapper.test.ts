import { describe, expect, it } from 'vitest';
import { z } from 'zod';
import { mapApiErrorToFields } from '@/lib/forms/api-error';
import { zodFieldValidator, zodFormValidator } from '@/lib/forms/zod-validator';
import { ApiError } from '@/lib/api/errors';
import { loginSchema } from '@/modules/auth/schemas';

describe('loginSchema', () => {
  it('rejects an empty email and password', () => {
    const result = loginSchema.safeParse({ email: '', password: '' });
    expect(result.success).toBe(false);
    if (!result.success) {
      const fields = result.error.flatten().fieldErrors;
      expect(fields.email?.[0]).toMatch(/valid email/i);
      expect(fields.password?.[0]).toMatch(/required/i);
    }
  });

  it('accepts a well-formed payload', () => {
    expect(loginSchema.safeParse({ email: 'a@b.test', password: 'x' }).success).toBe(true);
  });
});

describe('zodFormValidator', () => {
  it('returns undefined when the value is valid', () => {
    const validate = zodFormValidator(loginSchema);
    expect(validate({ value: { email: 'a@b.test', password: 'x' } })).toBeUndefined();
  });

  it('groups issues by top-level field path', () => {
    const validate = zodFormValidator(loginSchema);
    const out = validate({ value: { email: 'bad', password: '' } }) as {
      fields: Record<string, string>;
    };
    expect(out.fields.email).toMatch(/valid email/i);
    expect(out.fields.password).toMatch(/required/i);
  });
});

describe('zodFieldValidator', () => {
  it('returns the first issue message for an invalid scalar', () => {
    const validate = zodFieldValidator(z.string().min(3, 'Too short'));
    expect(validate({ value: 'ab' })).toBe('Too short');
  });

  it('returns undefined for a valid value', () => {
    const validate = zodFieldValidator(z.string().min(1));
    expect(validate({ value: 'ok' })).toBeUndefined();
  });
});

describe('mapApiErrorToFields', () => {
  function makeError(details: Record<string, unknown>) {
    return new ApiError({ code: 'API-400', message: 'Validation failed.', details }, 400);
  }

  it('reads errors from details.fields (preferred shape)', () => {
    const err = makeError({ fields: { email: 'Already taken' } });
    const out = mapApiErrorToFields(err);
    expect(out.fields).toEqual({ email: 'Already taken' });
    expect(out.formMessage).toBe('');
  });

  it('falls back to flat details (DRF ValidationError shape)', () => {
    const err = makeError({ email: ['Already taken'], password: ['Too short'] });
    const out = mapApiErrorToFields(err);
    expect(out.fields).toEqual({ email: 'Already taken', password: 'Too short' });
    expect(out.formMessage).toBe('');
  });

  it('keeps the form-level message when knownFields drops unknown keys', () => {
    const err = makeError({ fields: { stray: 'oops' } });
    const out = mapApiErrorToFields(err, { knownFields: ['email'] });
    expect(out.fields).toEqual({});
    expect(out.formMessage).toBe('Validation failed.');
  });

  it('returns a generic message for non-ApiError values', () => {
    const out = mapApiErrorToFields(new Error('boom'));
    expect(out.fields).toEqual({});
    expect(out.formMessage).toBe('boom');
  });
});
