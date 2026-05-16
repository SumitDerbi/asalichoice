import { z } from 'zod';

/**
 * Zod schemas for the auth module. Co-located here so both the login form
 * and any future password-reset / change-password flows share the same
 * validation rules.
 */
export const loginSchema = z.object({
  email: z.string().email('Enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
});

export type LoginValues = z.infer<typeof loginSchema>;
