import type { ColumnDef } from '@tanstack/react-table';
import { Field } from '@/lib/forms';
import { CatalogListPage } from '../components/catalog-list-page';
import { CatalogFormBody } from '../components/catalog-form-body';
import { CheckboxField, JsonField } from '../components/json-field';
import { useCanManageCatalog } from '../lib/use-permission';
import { variantSchema, type VariantInput } from '../schemas';
import type { ProductVariant } from '../api/types';
import { t } from '../lib/i18n';

const KNOWN = ['product', 'sku', 'barcode', 'attributes_json', 'is_default'] as const;

const columns: ColumnDef<ProductVariant, unknown>[] = [
  { accessorKey: 'product', header: () => t('common.product') },
  { accessorKey: 'sku', header: () => t('common.sku') },
  { accessorKey: 'barcode', header: () => 'Barcode' },
  {
    id: 'is_default',
    header: () => t('common.is_default'),
    cell: ({ row }) => (row.original.is_default ? '✓' : ''),
  },
];

export function VariantsPage() {
  const canManage = useCanManageCatalog();
  return (
    <CatalogListPage<ProductVariant, VariantInput>
      endpoint="variants"
      title={t('variants.title')}
      subtitle={t('variants.subtitle')}
      canManage={canManage}
      searchField={null}
      columns={columns}
      renderForm={({ initial, onSubmit, onCancel, submitting }) => (
        <CatalogFormBody<VariantInput>
          schema={variantSchema}
          defaultValues={{
            product: (initial.product ?? null) as unknown as number,
            sku: initial.sku ?? '',
            barcode: initial.barcode ?? '',
            attributes_json: initial.attributes_json ?? null,
            is_default: initial.is_default ?? false,
          }}
          knownFields={KNOWN}
          onSubmit={onSubmit}
          onCancel={onCancel}
          submitting={submitting}
        >
          {({ form, errorMap }) => (
            <>
              <form.Field name="product">
                {(f) => (
                  <Field field={f} label={`${t('common.product')} ID`} formErrorMap={errorMap} />
                )}
              </form.Field>
              <form.Field name="sku">
                {(f) => <Field field={f} label={t('common.sku')} formErrorMap={errorMap} />}
              </form.Field>
              <form.Field name="barcode">
                {(f) => <Field field={f} label="Primary barcode" formErrorMap={errorMap} />}
              </form.Field>
              <form.Field name="attributes_json">
                {(f) => (
                  <JsonField
                    field={f}
                    label={t('common.attributes_json')}
                    rows={4}
                    placeholder={'{\n  "color": "red"\n}'}
                    formErrorMap={errorMap}
                  />
                )}
              </form.Field>
              <form.Field name="is_default">
                {(f) => (
                  <CheckboxField field={f} label={t('common.is_default')} formErrorMap={errorMap} />
                )}
              </form.Field>
            </>
          )}
        </CatalogFormBody>
      )}
    />
  );
}
