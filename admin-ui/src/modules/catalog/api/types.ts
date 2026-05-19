/**
 * TypeScript shapes mirroring backend `apps.catalog` serializers.
 */

export interface BaseRow {
  id: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export type ProductStatus = 'DRAFT' | 'ACTIVE' | 'ARCHIVED';

export interface ProductVariant extends BaseRow {
  product: number;
  sku: string;
  barcode: string;
  attributes_json: unknown;
  image: string | null;
  is_default: boolean;
}

export interface ProductImage extends BaseRow {
  product: number;
  image: string;
  position: number;
  alt: string;
}

export interface Product extends BaseRow {
  code: string;
  sku: string;
  slug: string;
  name: string;
  brand: number | null;
  category: number;
  hsn: number | null;
  tax: number | null;
  base_uom: number;
  description: string;
  attributes_json: unknown;
  is_variant_parent: boolean;
  status: ProductStatus;
  seo_title: string;
  seo_description: string;
  seo_image: string | null;
  variants?: ProductVariant[];
  images?: ProductImage[];
}

export type BundleKind = 'COMBO' | 'MIX_AND_MATCH';
export type BundlePricePolicy = 'FIXED' | 'SUM';

export interface Bundle extends BaseRow {
  code: string;
  name: string;
  kind: BundleKind;
  price_policy: BundlePricePolicy;
  fixed_price: string | null;
}

export interface BundleComponent extends BaseRow {
  bundle: number;
  product: number;
  quantity: string;
}

export interface ProductPrice extends BaseRow {
  product: number | null;
  variant: number | null;
  branch: number;
  mrp: string;
  sale_price: string;
  cost_price: string | null;
  valid_from: string;
  valid_to: string | null;
}

export type BarcodeKind = 'EAN13' | 'UPC' | 'CODE128' | 'CUSTOM';

export interface Barcode extends BaseRow {
  value: string;
  type: BarcodeKind;
  product: number | null;
  variant: number | null;
}

export type AttributeKind = 'TEXT' | 'NUMBER' | 'BOOL' | 'SELECT';

export interface Attribute extends BaseRow {
  code: string;
  name: string;
  type: AttributeKind;
  options_json: unknown;
}

export interface ProductAttributeValue extends BaseRow {
  product: number;
  attribute: number;
  value: string;
}

export interface ProductBranchAvailability extends BaseRow {
  product: number;
  branch: number;
  is_listed: boolean;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
