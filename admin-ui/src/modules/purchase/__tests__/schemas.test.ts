import { describe, it, expect } from 'vitest';
import { vendorSchema, poSchema, invoiceFromGRNsSchema } from '../schemas';

describe('purchase schemas', () => {
  describe('vendorSchema', () => {
    it('accepts minimal valid input', () => {
      const r = vendorSchema.safeParse({ code: 'V1', name: 'Acme' });
      expect(r.success).toBe(true);
    });

    it('rejects empty code/name', () => {
      expect(vendorSchema.safeParse({ code: '', name: 'X' }).success).toBe(false);
      expect(vendorSchema.safeParse({ code: 'X', name: '' }).success).toBe(false);
    });

    it('validates GSTIN format when provided', () => {
      const good = vendorSchema.safeParse({
        code: 'V1',
        name: 'Acme',
        gstin: '27AAAPA1234A1Z5',
      });
      expect(good.success).toBe(true);

      const bad = vendorSchema.safeParse({ code: 'V1', name: 'Acme', gstin: 'NOTAGSTIN' });
      expect(bad.success).toBe(false);
    });

    it('allows empty GSTIN', () => {
      const r = vendorSchema.safeParse({ code: 'V1', name: 'Acme', gstin: '' });
      expect(r.success).toBe(true);
    });

    it('validates credit_limit as decimal string', () => {
      expect(
        vendorSchema.safeParse({ code: 'V1', name: 'Acme', credit_limit: '1000.00' }).success,
      ).toBe(true);
      expect(
        vendorSchema.safeParse({ code: 'V1', name: 'Acme', credit_limit: 'abc' }).success,
      ).toBe(false);
    });
  });

  describe('poSchema', () => {
    it('requires at least one item', () => {
      const r = poSchema.safeParse({
        po_no: 'PO-1',
        vendor: 1,
        branch: 1,
        items: [],
      });
      expect(r.success).toBe(false);
    });

    it('accepts a single line PO', () => {
      const r = poSchema.safeParse({
        po_no: 'PO-1',
        vendor: 1,
        branch: 1,
        items: [{ product: 1, uom: 1, qty: '10', rate: '100.50' }],
      });
      expect(r.success).toBe(true);
    });

    it('rejects non-decimal qty/rate', () => {
      const r = poSchema.safeParse({
        po_no: 'PO-1',
        vendor: 1,
        branch: 1,
        items: [{ product: 1, uom: 1, qty: 'ten', rate: '100' }],
      });
      expect(r.success).toBe(false);
    });
  });

  describe('invoiceFromGRNsSchema', () => {
    it('requires at least one GRN id', () => {
      const r = invoiceFromGRNsSchema.safeParse({
        vendor: 1,
        branch: 1,
        pi_no: 'PI-1',
        grn_ids: [],
      });
      expect(r.success).toBe(false);
    });

    it('accepts valid payload', () => {
      const r = invoiceFromGRNsSchema.safeParse({
        vendor: 1,
        branch: 1,
        pi_no: 'PI-1',
        grn_ids: [1, 2],
      });
      expect(r.success).toBe(true);
    });
  });
});
