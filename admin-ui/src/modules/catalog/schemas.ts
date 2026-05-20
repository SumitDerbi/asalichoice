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
  seo_title: z.string().max(255).optional().default(''),
  seo_description: z.string().optional().default(''),
  seo_image: z.string().url().nullable().optional(),
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

const requiredId = z.preprocess(
  (v) => (v === '' || v == null ? undefined : Number(v)),
  z.number().int().positive('Required'),
);
const optionalId = z.preprocess(
  (v) => (v === '' || v == null ? null : Number(v)),
  z.number().int().positive().nullable(),
);

export const variantSchema = z.object({
  product: requiredId,
  sku: z.string().min(1, 'Required').max(64),
  barcode: z.string().max(64).optional().default(''),
  // Backend `attributes_json` is a JSONField(default=dict, null=False).
  // Empty textarea → null in the form; coerce to {} so POST doesn't 400 with
  // "This field may not be null."
  attributes_json: z.preprocess((v) => (v == null ? {} : v), z.unknown()),
  is_default: z.boolean().optional().default(false),
});

export type VariantInput = z.infer<typeof variantSchema>;

export const barcodeSchema = z
  .object({
    value: z.string().min(1, 'Required').max(64),
    type: z.enum(['EAN13', 'UPC', 'CODE128', 'CUSTOM']),
    product: optionalId,
    variant: optionalId,
  })
  .refine((v) => Boolean(v.product) !== Boolean(v.variant), {
    message: 'Pick exactly one of product or variant',
    path: ['product'],
  });

export type BarcodeInput = z.infer<typeof barcodeSchema>;

export const attributeSchema = z.object({
  code: z.string().min(1, 'Required').max(64),
  name: z.string().min(1, 'Required').max(120),
  type: z.enum(['TEXT', 'NUMBER', 'BOOL', 'SELECT']),
  options_json: z.unknown().optional(),
});

export type AttributeInput = z.infer<typeof attributeSchema>;

export const availabilitySchema = z.object({
  product: requiredId,
  branch: requiredId,
  is_listed: z.boolean().optional().default(true),
});

export type AvailabilityInput = z.infer<typeof availabilitySchema>;
