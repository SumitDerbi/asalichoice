import { describe, expect, it } from 'vitest';
import {
  branchSchema,
  brandSchema,
  categorySchema,
  countrySchema,
  departmentSchema,
  hsnSchema,
  paymentModeSchema,
  pincodeSchema,
  stateSchema,
  taxSchema,
  uomSchema,
  warehouseSchema,
  zoneSchema,
} from '@/modules/masters/schemas';

describe('master schemas', () => {
  it('departmentSchema requires code and name', () => {
    expect(departmentSchema.safeParse({ code: '', name: 'X' }).success).toBe(false);
    expect(departmentSchema.safeParse({ code: 'A', name: '' }).success).toBe(false);
    const ok = departmentSchema.safeParse({ code: 'OPS', name: 'Operations', description: '' });
    expect(ok.success).toBe(true);
  });

  it('countrySchema enforces ISO lengths', () => {
    expect(countrySchema.safeParse({ iso2: 'IN', iso3: 'IND', name: 'India' }).success).toBe(true);
    expect(countrySchema.safeParse({ iso2: 'I', iso3: 'IND', name: 'India' }).success).toBe(false);
    expect(countrySchema.safeParse({ iso2: 'IN', iso3: 'IN', name: 'India' }).success).toBe(false);
  });

  it('stateSchema requires country FK', () => {
    expect(
      stateSchema.safeParse({ country: 1, code: 'MH', name: 'Maharashtra', gst_state_code: '27' })
        .success,
    ).toBe(true);
    expect(stateSchema.safeParse({ country: 0, code: 'MH', name: 'Maharashtra' }).success).toBe(
      false,
    );
  });

  it('branchSchema validates type enum and rejects bad email', () => {
    expect(
      branchSchema.safeParse({
        code: 'HQ',
        name: 'HQ',
        type: 'HQ',
        email: 'not-an-email',
      }).success,
    ).toBe(false);
    expect(
      branchSchema.safeParse({
        code: 'HQ',
        name: 'HQ',
        type: 'INVALID',
      }).success,
    ).toBe(false);
  });

  it('taxSchema requires at least one component', () => {
    expect(taxSchema.safeParse({ code: 'GST5', name: 'GST 5%', components_json: [] }).success).toBe(
      false,
    );
    expect(
      taxSchema.safeParse({
        code: 'GST5',
        name: 'GST 5%',
        components_json: [{ type: 'CGST', rate: '2.5' }],
      }).success,
    ).toBe(true);
  });

  it('uomSchema validates conversion_factor as positive decimal', () => {
    expect(
      uomSchema.safeParse({ code: 'KG', name: 'Kilogram', conversion_factor: '-1' }).success,
    ).toBe(false);
    expect(
      uomSchema.safeParse({ code: 'KG', name: 'Kilogram', conversion_factor: '0.5' }).success,
    ).toBe(true);
  });

  it('warehouseSchema requires branch', () => {
    expect(warehouseSchema.safeParse({ code: 'W1', name: 'W1', branch: 0 }).success).toBe(false);
    expect(warehouseSchema.safeParse({ code: 'W1', name: 'W1', branch: 1 }).success).toBe(true);
  });

  it('zoneSchema requires branch and defaults arrays', () => {
    const ok = zoneSchema.safeParse({ code: 'Z1', name: 'Zone 1', branch: 1 });
    expect(ok.success).toBe(true);
    if (ok.success) {
      expect(ok.data.pincodes).toEqual([]);
      expect(ok.data.pincode_ranges_json).toEqual([]);
    }
  });

  it('pincodeSchema accepts plain code', () => {
    expect(pincodeSchema.safeParse({ code: '400001' }).success).toBe(true);
    expect(pincodeSchema.safeParse({ code: 'ab' }).success).toBe(false);
  });

  it('paymentModeSchema validates kind enum', () => {
    expect(paymentModeSchema.safeParse({ code: 'CSH', name: 'Cash', type: 'CASH' }).success).toBe(
      true,
    );
    expect(paymentModeSchema.safeParse({ code: 'X', name: 'Cash', type: 'XYZ' }).success).toBe(
      false,
    );
  });

  it('categorySchema accepts optional parent and slug', () => {
    expect(categorySchema.safeParse({ code: 'GR', name: 'Grocery' }).success).toBe(true);
  });

  it('brandSchema validates basic fields', () => {
    expect(brandSchema.safeParse({ code: 'B1', name: 'Brand 1' }).success).toBe(true);
  });

  it('hsnSchema accepts code only', () => {
    expect(hsnSchema.safeParse({ code: '1001' }).success).toBe(true);
    expect(hsnSchema.safeParse({ code: '' }).success).toBe(false);
  });
});
