import type { ColumnDef } from '@tanstack/react-table';
import { Field } from '@/lib/forms';
import { CatalogListPage } from '../components/catalog-list-page';
import { CatalogFormBody } from '../components/catalog-form-body';
import { SelectField } from '@/modules/masters/components/select-field';
import { ProductSelectField, VariantSelectField } from '../components/catalog-select-field';
import { useCanManageCatalog } from '../lib/use-permission';
import { barcodeSchema, type BarcodeInput } from '../schemas';
import type { Barcode } from '../api/types';
import { t } from '../lib/i18n';

const KNOWN = ['value', 'type', 'product', 'variant'] as const;

const TYPE_OPTS = [
  { value: 'EAN13', label: 'EAN-13' },
  { value: 'UPC', label: 'UPC' },
  { value: 'CODE128', label: 'Code128' },
  { value: 'CUSTOM', label: 'Custom' },
];

const TYPE_FILTER = TYPE_OPTS.map((o) => ({ value: o.value, label: o.label }));

const columns: ColumnDef<Barcode, unknown>[] = [
  { accessorKey: 'value', header: () => t('common.value') },
  { accessorKey: 'type', header: () => t('common.type') },
  {
    id: 'target',
    header: () => 'Target',
    cell: ({ row }) =>
      row.original.product
        ? `Product #${row.original.product}`
        : row.original.variant
          ? `Variant #${row.original.variant}`
          : '—',
  },
];

export function BarcodesPage() {
  const canManage = useCanManageCatalog();
  return (
    <CatalogListPage<Barcode, BarcodeInput>
      endpoint="barcodes"
      title={t('barcodes.title')}
      subtitle={t('barcodes.subtitle')}
      canManage={canManage}
      searchField="search"
      filters={[{ label: t('common.type'), param: 'type', options: TYPE_FILTER }]}
      columns={columns}
      renderForm={({ initial, onSubmit, onCancel, submitting }) => (
        <CatalogFormBody<BarcodeInput>
          schema={barcodeSchema}
          defaultValues={{
            value: initial.value ?? '',
            type: initial.type ?? 'EAN13',
            product: initial.product ?? null,
            variant: initial.variant ?? null,
          }}
          knownFields={KNOWN}
          onSubmit={onSubmit}
          onCancel={onCancel}
          submitting={submitting}
        >
          {({ form, errorMap }) => (
            <>
              <form.Field name="value">
                {(f) => <Field field={f} label={t('common.value')} formErrorMap={errorMap} />}
              </form.Field>
              <form.Field name="type">
                {(f) => (
                  <SelectField
                    field={f}
                    label={t('common.type')}
                    options={TYPE_OPTS}
                    formErrorMap={errorMap}
                  />
                )}
              </form.Field>
              <form.Field name="product">
                {(f) => (
                  <ProductSelectField
                    field={f}
                    label={`${t('common.product')} (exclusive with variant)`}
                    allowEmpty
                    formErrorMap={errorMap}
                  />
                )}
              </form.Field>
              <form.Field name="variant">
                {(f) => (
                  <VariantSelectField
                    field={f}
                    label={`${t('common.variant')} (exclusive with product)`}
                    allowEmpty
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
