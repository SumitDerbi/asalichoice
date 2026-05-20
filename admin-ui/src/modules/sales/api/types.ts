export interface Paginated<T> {
  count?: number;
  next?: string | null;
  previous?: string | null;
  results: T[];
}

export type SaleOrigin = 'POS' | 'ONLINE' | 'B2B' | 'MANUAL';
export type SaleStatus =
  | 'DRAFT'
  | 'HELD'
  | 'CONFIRMED'
  | 'PARTIALLY_PAID'
  | 'PAID'
  | 'CANCELLED'
  | 'REFUNDED';
export type TaxMode = 'INCLUSIVE' | 'EXCLUSIVE';
export type SalePaymentStatus = 'PENDING' | 'SUCCESS' | 'FAILED' | 'REFUNDED';
export type DiscountScope = 'HEADER' | 'LINE';
export type DiscountKind = 'PERCENT' | 'FLAT';

export interface SaleItem {
  id: number;
  product: number | null;
  variant: number | null;
  uom: number;
  batch: number | null;
  hsn: number | null;
  tax: number | null;
  qty: string;
  mrp: string;
  sale_price: string;
  discount_amount: string;
  line_subtotal: string;
  line_total: string;
  tax_breakup_json: unknown;
}

export interface SalePayment {
  id: number;
  payment_mode: number;
  amount: string;
  ref_no: string;
  gateway_txn: string;
  status: SalePaymentStatus;
  at: string;
}

export interface Sale {
  id: number;
  sale_no: string;
  origin: SaleOrigin;
  branch: number;
  customer: number | null;
  cashier: number | null;
  terminal_id_external: number | null;
  status: SaleStatus;
  tax_mode: TaxMode;
  billed_at: string | null;
  cancelled_at: string | null;
  subtotal: string;
  discount_total: string;
  tax_total: string;
  grand_total: string;
  payment_total: string;
  totals_json: Record<string, string>;
  notes: string;
  offline_uuid: string | null;
  items: SaleItem[];
  payments: SalePayment[];
  created_at: string;
  updated_at: string;
}

export interface Discount {
  id: number;
  code: string;
  name: string;
  scope: DiscountScope;
  kind: DiscountKind;
  value: string;
  condition_json: Record<string, unknown>;
  requires_approval: boolean;
  is_active: boolean;
}
