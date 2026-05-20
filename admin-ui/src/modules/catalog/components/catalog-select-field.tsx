import * as React from 'react';
import type { FieldApi } from '@tanstack/react-form';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { SelectField } from '@/modules/masters/components/select-field';
import { useCatalogList } from '../api/hooks';
import type { Product, ProductVariant } from '../api/types';

/**
 * Async `<select>` for catalog FK pickers (Product / Variant). Mirrors
 * `RemoteSelectField` in masters but talks to `/api/v1/catalog/*` via
 * `useCatalogList`. Use these instead of raw "Product ID" text inputs so
 * users get a searchable list of human labels rather than typing numeric
 * primary keys.
 */

interface CatalogSelectProps {
  field: FieldApi<any, any, any, any>; // eslint-disable-line @typescript-eslint/no-explicit-any
  label: React.ReactNode;
  allowEmpty?: boolean;
  emptyLabel?: string;
  formErrorMap?: Record<string, unknown>;
}

export function ProductSelectField({
  field,
  label,
  allowEmpty = false,
  emptyLabel,
  formErrorMap,
}: CatalogSelectProps) {
  const { data, isLoading } = useCatalogList<Product>('products');
  const options = React.useMemo(
    () =>
      (data ?? []).map((row) => ({
        value: row.id,
        label: `${row.code} — ${row.name}`,
      })),
    [data],
  );
  if (isLoading) {
    return (
      <div className="space-y-1.5">
        <Label>{label}</Label>
        <Input disabled placeholder="Loading…" />
      </div>
    );
  }
  return (
    <SelectField
      field={field}
      label={label}
      options={options}
      allowEmpty={allowEmpty}
      emptyLabel={emptyLabel ?? '—'}
      formErrorMap={formErrorMap}
    />
  );
}

interface VariantSelectProps extends CatalogSelectProps {
  /** Optional product filter so the variant list narrows to one parent. */
  productId?: number | null;
}

export function VariantSelectField({
  field,
  label,
  productId,
  allowEmpty = false,
  emptyLabel,
  formErrorMap,
}: VariantSelectProps) {
  const params = productId ? { product: productId } : undefined;
  const { data, isLoading } = useCatalogList<ProductVariant>('variants', params);
  const options = React.useMemo(
    () =>
      (data ?? []).map((row) => ({
        value: row.id,
        label: row.sku || `Variant #${row.id}`,
      })),
    [data],
  );
  if (isLoading) {
    return (
      <div className="space-y-1.5">
        <Label>{label}</Label>
        <Input disabled placeholder="Loading…" />
      </div>
    );
  }
  return (
    <SelectField
      field={field}
      label={label}
      options={options}
      allowEmpty={allowEmpty}
      emptyLabel={emptyLabel ?? '—'}
      formErrorMap={formErrorMap}
    />
  );
}
