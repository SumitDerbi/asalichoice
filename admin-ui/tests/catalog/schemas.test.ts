import { describe, expect, it } from 'vitest';
import { bundleSchema, priceSchema, productSchema } from '@/modules/catalog/schemas';

describe('catalog schemas', () => {
  it('productSchema requires core fields', () => {
    const bad = productSchema.safeParse({ code: '', sku: '', slug: '', name: '' });
    expect(bad.success).toBe(false);
    const ok = productSchema.safeParse({
      code: 'P-1',
      sku: 'S-1',
      slug: 'p-1',
      name: 'Item',
      category: 1,
      base_uom: 1,
    });
    expect(ok.success).toBe(true);
  });

  it('bundleSchema requires fixed_price when policy=FIXED', () => {
    expect(
      bundleSchema.safeParse({
        code: 'B1',
        name: 'B1',
        kind: 'COMBO',
        price_policy: 'FIXED',
      }).success,
    ).toBe(false);
    expect(
      bundleSchema.safeParse({
        code: 'B1',
        name: 'B1',
        kind: 'COMBO',
        price_policy: 'FIXED',
        fixed_price: '99.00',
      }).success,
    ).toBe(true);
    expect(
      bundleSchema.safeParse({
        code: 'B2',
        name: 'B2',
        kind: 'COMBO',
        price_policy: 'SUM',
      }).success,
    ).toBe(true);
  });

  it('priceSchema enforces XOR product/variant', () => {
    const both = priceSchema.safeParse({
      product: 1,
      variant: 1,
      branch: 1,
      mrp: '10.00',
      sale_price: '9.00',
      valid_from: '2026-01-01T00:00',
    });
    expect(both.success).toBe(false);

    const neither = priceSchema.safeParse({
      branch: 1,
      mrp: '10.00',
      sale_price: '9.00',
      valid_from: '2026-01-01T00:00',
    });
    expect(neither.success).toBe(false);

    const ok = priceSchema.safeParse({
      product: 1,
      branch: 1,
      mrp: '10.00',
      sale_price: '9.00',
      valid_from: '2026-01-01T00:00',
    });
    expect(ok.success).toBe(true);
  });

  it('priceSchema rejects non-decimal strings', () => {
    expect(
      priceSchema.safeParse({
        product: 1,
        branch: 1,
        mrp: 'abc',
        sale_price: '9.00',
        valid_from: '2026-01-01T00:00',
      }).success,
    ).toBe(false);
  });
});
