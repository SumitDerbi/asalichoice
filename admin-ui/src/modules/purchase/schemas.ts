import { z } from 'zod';

export const vendorSchema = z.object({
  code: z.string().min(1, 'Required').max(64),
  name: z.string().min(1, 'Required').max(240),
  contact_name: z.string().max(160).optional().default(''),
  contact_email: z
    .union([z.string().email(), z.literal('')])
    .optional()
    .default(''),
  contact_mobile: z.string().max(20).optional().default(''),
  gstin: z
    .union([
      z.string().regex(/^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][0-9A-Z]Z[0-9A-Z]$/, 'Invalid GSTIN'),
      z.literal(''),
    ])
    .optional()
    .default(''),
  pan: z.string().max(20).optional().default(''),
  credit_limit: z
    .string()
    .regex(/^\d+(\.\d{1,2})?$/, 'Must be decimal')
    .default('0'),
});

export type VendorInput = z.infer<typeof vendorSchema>;

const decimal = (msg = 'Must be decimal') => z.string().regex(/^\d+(\.\d{1,4})?$/, msg);

export const poItemSchema = z.object({
  product: z.number().int().positive().nullable().optional(),
  variant: z.number().int().positive().nullable().optional(),
  uom: z.number().int().positive(),
  qty: decimal(),
  rate: decimal(),
  tax: z.number().int().positive().nullable().optional(),
  discount: decimal().optional().default('0'),
});

export const poSchema = z.object({
  po_no: z.string().min(1).max(64),
  vendor: z.number().int().positive(),
  branch: z.number().int().positive(),
  expected_delivery: z.string().nullable().optional(),
  terms: z.string().optional().default(''),
  items: z.array(poItemSchema).min(1, 'At least one line item is required'),
});

export type POInput = z.infer<typeof poSchema>;

export const grnItemSchema = z.object({
  po_item: z.number().int().positive().nullable().optional(),
  product: z.number().int().positive().nullable().optional(),
  variant: z.number().int().positive().nullable().optional(),
  qty_received: decimal(),
  qty_accepted: decimal().optional(),
  qty_rejected: decimal().optional().default('0'),
  rejection_reason: z.string().max(255).optional().default(''),
  batch_no: z.string().max(64).optional().default(''),
  mfg_date: z.string().nullable().optional(),
  expiry_date: z.string().nullable().optional(),
  cost_price: decimal().default('0'),
});

export const grnSchema = z.object({
  grn_no: z.string().min(1).max(64),
  po: z.number().int().positive().nullable().optional(),
  vendor: z.number().int().positive(),
  branch: z.number().int().positive(),
  received_at: z.string().nullable().optional(),
  vehicle_no: z.string().max(40).optional().default(''),
  transporter: z.string().max(160).optional().default(''),
  items: z.array(grnItemSchema).min(1, 'At least one line item is required'),
});

export type GRNInput = z.infer<typeof grnSchema>;

export const invoiceFromGRNsSchema = z.object({
  vendor: z.number().int().positive(),
  branch: z.number().int().positive(),
  pi_no: z.string().min(1).max(64),
  grn_ids: z.array(z.number().int().positive()).min(1),
  invoice_no_vendor: z.string().max(64).optional().default(''),
  invoice_date: z.string().nullable().optional(),
  due_date: z.string().nullable().optional(),
  payment_terms: z.string().max(120).optional().default(''),
});

export type InvoiceFromGRNsInput = z.infer<typeof invoiceFromGRNsSchema>;
