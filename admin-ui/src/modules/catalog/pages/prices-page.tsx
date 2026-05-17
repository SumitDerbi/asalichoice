import type { ColumnDef } from '@tanstack/react-table';
import { Field } from '@/lib/forms';
import { CatalogListPage } from '../components/catalog-list-page';
import { CatalogFormBody } from '../components/catalog-form-body';
import { RemoteSelectField } from '@/modules/masters/components/select-field';
import { useCanManagePrices } from '../lib/use-permission';
import { priceSchema, type PriceInput } from '../schemas';
import type { ProductPrice } from '../api/types';
import { t } from '../lib/i18n';

const KNOWN = [
  'product',
  'variant',
  'branch',
  'mrp',
  'sale_price',
  'cost_price',
  'valid_from',
  'valid_to',
] as const;

const columns: ColumnDef<ProductPrice, unknown>[] = [
  { accessorKey: 'product', header: () => 'Product' },
  { accessorKey: 'variant', header: () => 'Variant' },
  { accessorKey: 'branch', header: () => t('common.branch') },
  { accessorKey: 'mrp', header: () => t('common.mrp') },
  { accessorKey: 'sale_price', header: () => t('common.sale_price') },
  { accessorKey: 'valid_from', header: () => t('common.valid_from') },
  { accessorKey: 'valid_to', header: () => t('common.valid_to') },
];

export function PricesPage() {
  const canManage = useCanManagePrices();
  return (
    <CatalogListPage<ProductPrice, PriceInput>
      endpoint="prices"
      title={t('prices.title')}
      canManage={canManage}
      searchField={null}
      columns={columns}
      renderForm={({ initial, onSubmit, onCancel, submitting }) => (
        <CatalogFormBody<PriceInput>
          schema={priceSchema}
          defaultValues={{
            product: initial.product ?? null,
            variant: initial.variant ?? null,
            branch: (initial.branch ?? 0) as number,
            mrp: initial.mrp ?? '0.00',
            sale_price: initial.sale_price ?? '0.00',
            cost_price: initial.cost_price ?? null,
            valid_from: (initial.valid_from ?? new Date().toISOString().slice(0, 16)) as string,
            valid_to: initial.valid_to ?? null,
          }}
          knownFields={KNOWN}
          onSubmit={onSubmit}
          onCancel={onCancel}
          submitting={submitting}
        >
          {({ form, errorMap }) => (
            <>
              <form.Field name="branch">
                {(f) => (
                  <RemoteSelectField
                    field={f}
                    label={t('common.branch')}
                    endpoint="branches"
                    getLabel={(r) => `${r.code} — ${r.name}`}
                    allowEmpty={false}
                    formErrorMap={errorMap}
                  />
                )}
              </form.Field>
              <form.Field name="product">
                {(f) => (
                  <Field
                    field={f}
                    label="Product ID (exclusive with variant)"
                    formErrorMap={errorMap}
                  />
                )}
              </form.Field>
              <form.Field name="variant">
                {(f) => (
                  <Field
                    field={f}
                    label="Variant ID (exclusive with product)"
                    formErrorMap={errorMap}
                  />
                )}
              </form.Field>
              <form.Field name="mrp">
                {(f) => <Field field={f} label={t('common.mrp')} formErrorMap={errorMap} />}
              </form.Field>
              <form.Field name="sale_price">
                {(f) => <Field field={f} label={t('common.sale_price')} formErrorMap={errorMap} />}
              </form.Field>
              <form.Field name="cost_price">
                {(f) => <Field field={f} label={t('common.cost_price')} formErrorMap={errorMap} />}
              </form.Field>
              <form.Field name="valid_from">
                {(f) => <Field field={f} label={t('common.valid_from')} formErrorMap={errorMap} />}
              </form.Field>
              <form.Field name="valid_to">
                {(f) => (
                  <Field
                    field={f}
                    label={`${t('common.valid_to')} (optional)`}
                    formErrorMap={errorMap}
                  />
                )}
              </form.Field>
            </>
          )}
        </CatalogFormBody>
      )}
    />
  );
}
