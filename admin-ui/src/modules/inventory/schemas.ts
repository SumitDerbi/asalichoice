import { z } from 'zod';

const decimal = (msg = 'Must be decimal') => z.string().regex(/^-?\d+(\.\d{1,4})?$/, msg);
const positiveDecimal = (msg = 'Must be positive decimal') =>
  z.string().regex(/^\d+(\.\d{1,4})?$/, msg);

export const reservationSchema = z
  .object({
    product: z.number().int().positive().nullable().optional(),
    variant: z.number().int().positive().nullable().optional(),
    branch: z.number().int().positive(),
    qty: positiveDecimal(),
    ref_type: z.enum(['ORDER', 'HOLD']),
    ref_id: z.string().min(1).max(64),
    expires_at: z.string().nullable().optional(),
  })
  .refine((v) => !!v.product !== !!v.variant, {
    message: 'Provide exactly one of product or variant',
    path: ['product'],
  });

export type ReservationInput = z.infer<typeof reservationSchema>;

export const transferItemSchema = z
  .object({
    product: z.number().int().positive().nullable().optional(),
    variant: z.number().int().positive().nullable().optional(),
    qty_sent: positiveDecimal(),
    qty_received: positiveDecimal().optional(),
  })
  .refine((v) => !!v.product !== !!v.variant, {
    message: 'Provide exactly one of product or variant',
    path: ['product'],
  });

export const transferSchema = z.object({
  tr_no: z.string().min(1).max(64),
  from_branch: z.number().int().positive(),
  to_branch: z.number().int().positive(),
  remarks: z.string().optional().default(''),
  items: z.array(transferItemSchema).min(1, 'At least one line item is required'),
});

export type TransferInput = z.infer<typeof transferSchema>;

export const adjustmentItemSchema = z
  .object({
    product: z.number().int().positive().nullable().optional(),
    variant: z.number().int().positive().nullable().optional(),
    qty_change: decimal(),
    reason_code: z.string().min(1).max(32),
  })
  .refine((v) => !!v.product !== !!v.variant, {
    message: 'Provide exactly one of product or variant',
    path: ['product'],
  });

export const adjustmentSchema = z.object({
  doc_no: z.string().min(1).max(64),
  branch: z.number().int().positive(),
  remarks: z.string().optional().default(''),
  items: z.array(adjustmentItemSchema).min(1, 'At least one line item is required'),
});

export type AdjustmentInput = z.infer<typeof adjustmentSchema>;

export const wastageItemSchema = z
  .object({
    product: z.number().int().positive().nullable().optional(),
    variant: z.number().int().positive().nullable().optional(),
    qty: positiveDecimal(),
    reason_code: z.string().min(1).max(32),
  })
  .refine((v) => !!v.product !== !!v.variant, {
    message: 'Provide exactly one of product or variant',
    path: ['product'],
  });

export const wastageSchema = z.object({
  doc_no: z.string().min(1).max(64),
  branch: z.number().int().positive(),
  remarks: z.string().optional().default(''),
  items: z.array(wastageItemSchema).min(1, 'At least one line item is required'),
});

export type WastageInput = z.infer<typeof wastageSchema>;

export const countItemSchema = z
  .object({
    product: z.number().int().positive().nullable().optional(),
    variant: z.number().int().positive().nullable().optional(),
    qty_counted: positiveDecimal(),
  })
  .refine((v) => !!v.product !== !!v.variant, {
    message: 'Provide exactly one of product or variant',
    path: ['product'],
  });

export const countSchema = z.object({
  doc_no: z.string().min(1).max(64),
  branch: z.number().int().positive(),
  remarks: z.string().optional().default(''),
  items: z.array(countItemSchema).min(1, 'At least one line item is required'),
});

export type CountInput = z.infer<typeof countSchema>;
