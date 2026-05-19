import { describe, it, expect } from 'vitest';
import {
  reservationSchema,
  transferSchema,
  adjustmentSchema,
  wastageSchema,
  countSchema,
} from '../schemas';

describe('inventory schemas', () => {
  describe('reservationSchema', () => {
    it('accepts minimal valid input', () => {
      const r = reservationSchema.safeParse({
        product: 1,
        branch: 1,
        qty: '2',
        ref_type: 'ORDER',
        ref_id: 'SO-1',
      });
      expect(r.success).toBe(true);
    });

    it('rejects when both product and variant are provided', () => {
      const r = reservationSchema.safeParse({
        product: 1,
        variant: 2,
        branch: 1,
        qty: '2',
        ref_type: 'ORDER',
        ref_id: 'SO-1',
      });
      expect(r.success).toBe(false);
    });

    it('rejects when neither product nor variant is provided', () => {
      const r = reservationSchema.safeParse({
        branch: 1,
        qty: '2',
        ref_type: 'ORDER',
        ref_id: 'SO-1',
      });
      expect(r.success).toBe(false);
    });

    it('rejects non-positive qty', () => {
      const r = reservationSchema.safeParse({
        product: 1,
        branch: 1,
        qty: '-1',
        ref_type: 'ORDER',
        ref_id: 'SO-1',
      });
      expect(r.success).toBe(false);
    });
  });

  describe('transferSchema', () => {
    it('accepts a valid transfer with one item', () => {
      const r = transferSchema.safeParse({
        tr_no: 'TR-1',
        from_branch: 1,
        to_branch: 2,
        items: [{ product: 5, qty_sent: '3' }],
      });
      expect(r.success).toBe(true);
    });

    it('rejects empty items array', () => {
      const r = transferSchema.safeParse({
        tr_no: 'TR-1',
        from_branch: 1,
        to_branch: 2,
        items: [],
      });
      expect(r.success).toBe(false);
    });
  });

  describe('adjustmentSchema', () => {
    it('accepts negative qty_change', () => {
      const r = adjustmentSchema.safeParse({
        doc_no: 'ADJ-1',
        branch: 1,
        items: [{ product: 5, qty_change: '-2', reason_code: 'DAMAGED' }],
      });
      expect(r.success).toBe(true);
    });

    it('requires reason_code on items', () => {
      const r = adjustmentSchema.safeParse({
        doc_no: 'ADJ-1',
        branch: 1,
        items: [{ product: 5, qty_change: '1', reason_code: '' }],
      });
      expect(r.success).toBe(false);
    });
  });

  describe('wastageSchema', () => {
    it('rejects negative qty', () => {
      const r = wastageSchema.safeParse({
        doc_no: 'W-1',
        branch: 1,
        items: [{ product: 5, qty: '-1', reason_code: 'EXPIRED' }],
      });
      expect(r.success).toBe(false);
    });

    it('accepts a positive qty wastage row', () => {
      const r = wastageSchema.safeParse({
        doc_no: 'W-1',
        branch: 1,
        items: [{ product: 5, qty: '1', reason_code: 'EXPIRED' }],
      });
      expect(r.success).toBe(true);
    });
  });

  describe('countSchema', () => {
    it('accepts a row with counted qty only (expected is server-stamped)', () => {
      const r = countSchema.safeParse({
        doc_no: 'PC-1',
        branch: 1,
        items: [{ product: 5, qty_counted: '10' }],
      });
      expect(r.success).toBe(true);
    });
  });
});
