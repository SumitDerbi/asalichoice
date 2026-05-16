/**
 * TypeScript shapes mirroring the backend `apps.master` serializers.
 * Keep field names aligned with DRF response keys.
 */

export interface BaseRow {
  id: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Country extends BaseRow {
  iso2: string;
  iso3: string;
  name: string;
  phone_code: string;
  currency_code: string;
}

export interface State extends BaseRow {
  country: number;
  country_iso2?: string;
  code: string;
  name: string;
  gst_state_code: string;
}

export interface City extends BaseRow {
  state: number;
  state_code?: string;
  name: string;
}

export interface Pincode extends BaseRow {
  code: string;
  city: number | null;
  latitude: string | null;
  longitude: string | null;
}

export type BranchType = 'HQ' | 'STORE' | 'WAREHOUSE' | 'DARK_STORE';

export interface Branch extends BaseRow {
  code: string;
  name: string;
  type: BranchType;
  parent: number | null;
  address: string;
  phone: string;
  email: string;
  feature_flags_json: Record<string, unknown>;
}

export interface Department extends BaseRow {
  code: string;
  name: string;
  description: string;
}

export interface Designation extends BaseRow {
  code: string;
  name: string;
  department: number | null;
}

export interface UnitOfMeasure extends BaseRow {
  code: string;
  name: string;
  symbol: string;
  parent: number | null;
  conversion_factor: string;
}

export type TaxComponentType = 'CGST' | 'SGST' | 'IGST' | 'CESS';

export interface TaxComponent {
  type: TaxComponentType;
  rate: string;
}

export interface Tax extends BaseRow {
  code: string;
  name: string;
  rate_total: string;
  components_json: TaxComponent[];
  hsn_codes: number[];
}

export interface HSNCode extends BaseRow {
  code: string;
  description: string;
  default_tax: number | null;
}

export type PaymentModeKind = 'CASH' | 'UPI' | 'CARD' | 'WALLET' | 'COD' | 'BANK';

export interface PaymentMode extends BaseRow {
  code: string;
  name: string;
  type: PaymentModeKind;
  branches: number[];
  config_json: Record<string, unknown>;
}

export interface Category extends BaseRow {
  code: string;
  name: string;
  parent: number | null;
  seo_slug: string;
  description: string;
  image: string | null;
}

export interface Brand extends BaseRow {
  code: string;
  name: string;
  description: string;
  logo: string | null;
}

export interface Warehouse extends BaseRow {
  code: string;
  name: string;
  branch: number;
  address: string;
}

export interface PincodeRange {
  from: string;
  to: string;
}

export interface Zone extends BaseRow {
  code: string;
  name: string;
  branch: number;
  pincodes: number[];
  pincode_ranges_json: PincodeRange[];
}

export interface TaxBreakup {
  base: string;
  tax_total: string;
  grand_total: string;
  components: Array<{ type: TaxComponentType; rate: string; amount: string }>;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
