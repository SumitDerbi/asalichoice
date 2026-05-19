/**
 * TypeScript shapes mirroring backend `apps.inventory` serializers (M05).
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

/** Cursor-paginated response from `/inventory/ledger/`. */
export interface CursorPage<T> {
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface Stock extends BaseRow {
  product: number | null;
  variant: number | null;
  branch: number;
  warehouse: number | null;
  qty_on_hand: string;
  qty_reserved: string;
  reorder_point: string;
}

export type BatchStatus = 'ACTIVE' | 'EXPIRED' | 'CONSUMED';

export interface Batch extends BaseRow {
  product: number | null;
  variant: number | null;
  branch: number;
  batch_no: string;
  mfg_date: string | null;
  expiry_date: string | null;
  cost_price: string;
  qty: string;
  status: BatchStatus;
}

export interface InventoryLedgerEntry {
  id: number;
  product: number | null;
  variant: number | null;
  branch: number;
  warehouse: number | null;
  batch: number | null;
  reference_type: string;
  reference_id: string;
  amount: string;
  balance_before: string;
  balance_after: string;
  reason_code: string;
  actor: number | null;
  timestamp: string;
  remarks: string;
}

export type ReservationStatus = 'ACTIVE' | 'RELEASED' | 'CONSUMED' | 'EXPIRED';

export interface Reservation extends BaseRow {
  product: number | null;
  variant: number | null;
  branch: number;
  qty: string;
  ref_type: 'ORDER' | 'HOLD';
  ref_id: string;
  expires_at: string | null;
  status: ReservationStatus;
}

export type BranchTransferStatus =
  | 'DRAFT'
  | 'IN_TRANSIT'
  | 'RECEIVED'
  | 'PART_RECEIVED'
  | 'CANCELLED';

export interface BranchTransferItem extends BaseRow {
  transfer: number;
  product: number | null;
  variant: number | null;
  qty_sent: string;
  qty_received: string;
  qty_lost: string;
}

export interface BranchTransfer extends BaseRow {
  tr_no: string;
  from_branch: number;
  to_branch: number;
  status: BranchTransferStatus;
  dispatched_at: string | null;
  received_at: string | null;
  remarks: string;
  items: BranchTransferItem[];
}

export type DocumentStatus = 'DRAFT' | 'POSTED' | 'CANCELLED';

export interface StockAdjustmentItem extends BaseRow {
  adjustment: number;
  product: number | null;
  variant: number | null;
  qty_change: string;
  reason_code: string;
}

export interface StockAdjustment extends BaseRow {
  doc_no: string;
  branch: number;
  status: DocumentStatus;
  posted_at: string | null;
  remarks: string;
  items: StockAdjustmentItem[];
}

export interface WastageItem extends BaseRow {
  wastage: number;
  product: number | null;
  variant: number | null;
  qty: string;
  reason_code: string;
}

export interface Wastage extends BaseRow {
  doc_no: string;
  branch: number;
  status: DocumentStatus;
  posted_at: string | null;
  remarks: string;
  items: WastageItem[];
}

export type PhysicalCountStatus = 'DRAFT' | 'COUNTED' | 'POSTED' | 'CANCELLED';

export interface PhysicalCountItem extends BaseRow {
  count: number;
  product: number | null;
  variant: number | null;
  qty_expected: string;
  qty_counted: string;
}

export interface PhysicalCount extends BaseRow {
  doc_no: string;
  branch: number;
  status: PhysicalCountStatus;
  counted_at: string | null;
  posted_at: string | null;
  remarks: string;
  items: PhysicalCountItem[];
}
