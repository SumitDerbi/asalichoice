import { z } from 'zod';

/**
 * Zod schemas for master entity create/edit forms. Field names mirror
 * DRF serializer fields. Server-side validation remains authoritative;
 * these schemas catch the common cases at the edge.
 */

const codeRule = z
  .string()
  .min(1, 'Code is required.')
  .max(32, 'Code is too long.')
  .regex(/^[A-Z0-9_-]+$/i, 'Letters, digits, dashes, underscores only.');

const nameRule = z.string().min(1, 'Name is required.').max(120, 'Name is too long.');

export const countrySchema = z.object({
  iso2: z.string().length(2, 'ISO-2 must be 2 characters.'),
  iso3: z.string().length(3, 'ISO-3 must be 3 characters.'),
  name: nameRule,
  phone_code: z.string().max(8).default(''),
  currency_code: z.string().max(3).default(''),
});
export type CountryInput = z.infer<typeof countrySchema>;

export const stateSchema = z.object({
  country: z.number().int().positive('Country is required.'),
  code: codeRule,
  name: nameRule,
  gst_state_code: z.string().max(4).default(''),
});
export type StateInput = z.infer<typeof stateSchema>;

export const citySchema = z.object({
  state: z.number().int().positive('State is required.'),
  name: nameRule,
});
export type CityInput = z.infer<typeof citySchema>;

export const pincodeSchema = z.object({
  code: z.string().min(3, 'Pincode is required.').max(10),
  city: z.union([z.number().int().positive(), z.null()]).optional(),
  latitude: z.string().optional().default(''),
  longitude: z.string().optional().default(''),
});
export type PincodeInput = z.infer<typeof pincodeSchema>;

export const branchSchema = z.object({
  code: codeRule,
  name: nameRule,
  type: z.enum(['HQ', 'STORE', 'WAREHOUSE', 'DARK_STORE']),
  parent: z.union([z.number().int().positive(), z.null()]).optional(),
  address: z.string().max(500).default(''),
  phone: z.string().max(20).default(''),
  email: z.string().email('Invalid email.').or(z.literal('')).default(''),
  feature_flags_json: z.record(z.unknown()).default({}),
});
export type BranchInput = z.infer<typeof branchSchema>;

export const departmentSchema = z.object({
  code: codeRule,
  name: nameRule,
  description: z.string().max(500).default(''),
});
export type DepartmentInput = z.infer<typeof departmentSchema>;

export const designationSchema = z.object({
  code: codeRule,
  name: nameRule,
  department: z.union([z.number().int().positive(), z.null()]).optional(),
});
export type DesignationInput = z.infer<typeof designationSchema>;

export const uomSchema = z.object({
  code: codeRule,
  name: nameRule,
  symbol: z.string().max(8).default(''),
  parent: z.union([z.number().int().positive(), z.null()]).optional(),
  conversion_factor: z
    .string()
    .regex(/^\d+(\.\d+)?$/, 'Must be a positive decimal.')
    .default('1'),
});
export type UomInput = z.infer<typeof uomSchema>;

export const taxComponentSchema = z.object({
  type: z.enum(['CGST', 'SGST', 'IGST', 'CESS']),
  rate: z.string().regex(/^\d+(\.\d+)?$/, 'Must be a decimal.'),
});

export const taxSchema = z.object({
  code: codeRule,
  name: nameRule,
  components_json: z.array(taxComponentSchema).min(1, 'At least one component is required.'),
});
export type TaxInput = z.infer<typeof taxSchema>;

export const hsnSchema = z.object({
  code: z.string().min(2, 'HSN code is required.').max(12),
  description: z.string().max(500).default(''),
  default_tax: z.union([z.number().int().positive(), z.null()]).optional(),
});
export type HsnInput = z.infer<typeof hsnSchema>;

export const paymentModeSchema = z.object({
  code: codeRule,
  name: nameRule,
  type: z.enum(['CASH', 'UPI', 'CARD', 'WALLET', 'COD', 'BANK']),
  branches: z.array(z.number().int().positive()).default([]),
  config_json: z.record(z.unknown()).default({}),
});
export type PaymentModeInput = z.infer<typeof paymentModeSchema>;

export const categorySchema = z.object({
  code: codeRule,
  name: nameRule,
  parent: z.union([z.number().int().positive(), z.null()]).optional(),
  seo_slug: z.string().max(120).default(''),
  description: z.string().max(500).default(''),
});
export type CategoryInput = z.infer<typeof categorySchema>;

export const brandSchema = z.object({
  code: codeRule,
  name: nameRule,
  description: z.string().max(500).default(''),
});
export type BrandInput = z.infer<typeof brandSchema>;

export const warehouseSchema = z.object({
  code: codeRule,
  name: nameRule,
  branch: z.number().int().positive('Branch is required.'),
  address: z.string().max(500).default(''),
});
export type WarehouseInput = z.infer<typeof warehouseSchema>;

export const zonePincodeRangeSchema = z.object({
  from: z.string().min(3),
  to: z.string().min(3),
});

export const zoneSchema = z.object({
  code: codeRule,
  name: nameRule,
  branch: z.number().int().positive('Branch is required.'),
  pincodes: z.array(z.number().int().positive()).default([]),
  pincode_ranges_json: z.array(zonePincodeRangeSchema).default([]),
});
export type ZoneInput = z.infer<typeof zoneSchema>;
