/**
 * TypeScript shapes mirroring backend `apps.purchase` serializers.
 */

export interface BaseRow {
  id: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface VendorContact extends BaseRow {
  vendor: number;
  name: string;
  role: string;
  email: string;
  mobile: string;
}

export interface VendorBankAccount extends BaseRow {
  vendor: number;
  account_no_masked: string;
  ifsc: string;
  bank_name: string;
  is_default: boolean;
}

export interface Vendor extends BaseRow {
  code: string;
  name: string;
  contact_name: string;
  contact_email: string;
  contact_mobile: string;
  gstin: string;
  pan: string;
  addresses_json: unknown[];
  payment_terms_json: Record<string, unknown>;
  credit_limit: string;
  branches: number[];
  contacts?: VendorContact[];
  bank_accounts?: VendorBankAccount[];
}

export type POStatus =
  | 'DRAFT'
  | 'PENDING_APPROVAL'
  | 'APPROVED'
  | 'PARTIAL'
  | 'RECEIVED'
  | 'CLOSED'
  | 'CANCELLED';

export interface POItem extends BaseRow {
  po: number;
  product: number | null;
  variant: number | null;
  qty: string;
  uom: number;
  rate: string;
  tax: number | null;
  discount: string;
  line_total: string;
}

export interface PurchaseOrder extends BaseRow {
  po_no: string;
  vendor: number;
  branch: number;
  status: POStatus;
  expected_delivery: string | null;
  terms: string;
  totals_json: Record<string, string>;
  approval_chain_json: string[];
  approved_by: number | null;
  approved_at: string | null;
  items?: POItem[];
}

export type GRNStatus = 'DRAFT' | 'SUBMITTED' | 'APPROVED' | 'REJECTED';

export interface GRNItem extends BaseRow {
  grn: number;
  po_item: number | null;
  product: number | null;
  variant: number | null;
  qty_received: string;
  qty_accepted: string;
  qty_rejected: string;
  rejection_reason: string;
  batch_no: string;
  mfg_date: string | null;
  expiry_date: string | null;
  cost_price: string;
}

export interface GRN extends BaseRow {
  grn_no: string;
  po: number | null;
  vendor: number;
  branch: number;
  status: GRNStatus;
  received_at: string | null;
  vehicle_no: string;
  transporter: string;
  offline_uuid: string | null;
  totals_json: Record<string, string>;
  items?: GRNItem[];
}

export type PIStatus = 'DRAFT' | 'POSTED' | 'PART_PAID' | 'PAID' | 'CANCELLED';

export interface PurchaseInvoice extends BaseRow {
  pi_no: string;
  vendor: number;
  branch: number;
  grns: number[];
  invoice_no_vendor: string;
  invoice_date: string | null;
  due_date: string | null;
  totals_json: Record<string, string>;
  status: PIStatus;
  payment_terms: string;
}

export type PRStatus = 'DRAFT' | 'POSTED' | 'CANCELLED';

export interface PurchaseReturn extends BaseRow {
  pr_no: string;
  grn: number;
  vendor: number;
  branch: number;
  reason: string;
  status: PRStatus;
  items_json: unknown[];
  totals_json: Record<string, string>;
}

export interface VendorLedgerEntry {
  id: number;
  vendor: number;
  branch: number | null;
  amount: string;
  balance_before: string;
  balance_after: string;
  reference_type: string;
  reference_id: string;
  remarks: string;
  timestamp: string;
}
