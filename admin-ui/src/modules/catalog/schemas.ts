import { z } from 'zod';

export const productSchema = z.object({
  code: z.string().min(1, 'Required').max(64),
  sku: z.string().min(1, 'Required').max(64),
  slug: z.string().min(1, 'Required').max(160),
  name: z.string().min(1, 'Required').max(255),
  brand: z.number().int().positive().nullable().optional(),
  category: z.number().int().positive(),
  hsn: z.number().int().positive().nullable().optional(),
  tax: z.number().int().positive().nullable().optional(),
  base_uom: z.number().int().positive(),
  description: z.string().optional().default(''),
  status: z.enum(['DRAFT', 'ACTIVE', 'ARCHIVED']).default('DRAFT'),
});

export type ProductInput = z.infer<typeof productSchema>;

export const bundleSchema = z
  .object({
    code: z.string().min(1).max(64),
    name: z.string().min(1).max(255),
    kind: z.enum(['COMBO', 'MIX_AND_MATCH']),
    price_policy: z.enum(['FIXED', 'SUM']),
    fixed_price: z
      .string()
      .regex(/^\d+(\.\d{1,2})?$/, 'Must be decimal')
      .nullable()
      .optional(),
  })
  .refine((v) => v.price_policy !== 'FIXED' || (v.fixed_price && v.fixed_price.length > 0), {
    message: 'fixed_price required when price_policy=FIXED',
    path: ['fixed_price'],
  });

export type BundleInput = z.infer<typeof bundleSchema>;

export const priceSchema = z
  .object({
    product: z.number().int().positive().nullable().optional(),
    variant: z.number().int().positive().nullable().optional(),
    branch: z.number().int().positive(),
    mrp: z.string().regex(/^\d+(\.\d{1,2})?$/, 'Must be decimal'),
    sale_price: z.string().regex(/^\d+(\.\d{1,2})?$/, 'Must be decimal'),
    cost_price: z
      .string()
      .regex(/^\d+(\.\d{1,2})?$/, 'Must be decimal')
      .nullable()
      .optional(),
    valid_from: z.string().min(1, 'Required'),
    valid_to: z.string().nullable().optional(),
  })
  .refine((v) => Boolean(v.product) !== Boolean(v.variant), {
    message: 'Pick exactly one of product or variant',
    path: ['product'],
  });

export type PriceInput = z.infer<typeof priceSchema>;
