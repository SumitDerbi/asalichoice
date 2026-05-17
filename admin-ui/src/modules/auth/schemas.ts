import { z } from 'zod';

/**
 * Zod schemas for the auth module. The login form takes a single
 * ``identifier`` field that the backend resolves to email, mobile, or
 * employee code (M02 multi-identifier identity).
 */
export const loginSchema = z.object({
  identifier: z.string().min(1, 'Enter email, mobile, or employee code'),
  password: z.string().min(1, 'Password is required'),
});

export type LoginValues = z.infer<typeof loginSchema>;

export const otpRequestSchema = z.object({
  identifier: z.string().min(1, 'Enter email, mobile, or employee code'),
});

export type OtpRequestValues = z.infer<typeof otpRequestSchema>;

export const otpVerifySchema = z.object({
  identifier: z.string().min(1),
  code: z.string().min(4, 'Enter the OTP code'),
});

export type OtpVerifyValues = z.infer<typeof otpVerifySchema>;
