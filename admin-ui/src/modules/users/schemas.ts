import { z } from 'zod';

export const userSchema = z.object({
  email: z.string().email('Enter a valid email'),
  mobile: z.string().nullable().optional(),
  employee_code: z.string().nullable().optional(),
  name: z.string().optional(),
  primary_identifier: z.enum(['EMAIL', 'MOBILE', 'EMP_CODE']).optional(),
  is_staff: z.boolean().optional(),
  is_active: z.boolean().optional(),
  password: z.string().min(8, 'At least 8 characters').optional().or(z.literal('')),
  role_ids: z.array(z.number()).optional(),
});

export type UserValues = z.infer<typeof userSchema>;

export const roleSchema = z.object({
  code: z.string().min(2, 'Code is required'),
  name: z.string().min(2, 'Name is required'),
  description: z.string().optional(),
  permission_ids: z.array(z.number()).optional(),
});

export type RoleValues = z.infer<typeof roleSchema>;

// Auth flows

export const otpRequestSchema = z.object({
  identifier: z.string().min(3, 'Enter your identifier'),
  preferred_channel: z.enum(['SMS', 'EMAIL', 'WHATSAPP']).optional(),
});
export type OTPRequestValues = z.infer<typeof otpRequestSchema>;

export const otpVerifySchema = z.object({
  identifier: z.string().min(3),
  code: z.string().min(4).max(8),
});
export type OTPVerifyValues = z.infer<typeof otpVerifySchema>;

export const passwordResetRequestSchema = z.object({
  identifier: z.string().min(3, 'Enter your identifier'),
  preferred_channel: z.enum(['SMS', 'EMAIL', 'WHATSAPP']).optional(),
});

export const passwordResetConfirmSchema = z
  .object({
    identifier: z.string().min(3),
    code: z.string().min(4).max(8),
    new_password: z.string().min(8, 'At least 8 characters'),
    confirm_password: z.string().min(8),
  })
  .refine((v) => v.new_password === v.confirm_password, {
    path: ['confirm_password'],
    message: 'Passwords do not match',
  });
