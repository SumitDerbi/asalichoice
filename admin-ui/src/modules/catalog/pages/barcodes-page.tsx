import * as React from 'react';
import type { ColumnDef } from '@tanstack/react-table';
import { Field } from '@/lib/forms';
import { CatalogListPage } from '../components/catalog-list-page';
import { CatalogFormBody } from '../components/catalog-form-body';
import { SelectField } from '@/modules/masters/components/select-field';
import { ProductSelectField, VariantSelectField } from '../components/catalog-select-field';
import { useCanManageCatalog } from '../lib/use-permission';
import { barcodeSchema, type BarcodeInput } from '../schemas';
import type { Barcode, Product, ProductVariant } from '../api/types';
import { useCatalogList } from '../api/hooks';
import { t } from '../lib/i18n';

const KNOWN = ['value', 'type', 'product', 'variant'] as const;

const TYPE_OPTS = [
  { value: 'EAN13', label: 'EAN-13' },
  { value: 'UPC', label: 'UPC' },
  { value: 'CODE128', label: 'Code128' },
  { value: 'CUSTOM', label: 'Custom' },
];

const TYPE_FILTER = TYPE_OPTS.map((o) => ({ value: o.value, label: o.label }));

function TargetCell({ row }: { row: Barcode }) {
  const { data: products } = useCatalogList<Product>('products');
  const { data: variants } = useCatalogList<ProductVariant>('variants');
  if (row.product) {
    const p = (products ?? []).find((r) => r.id === row.product);
    return <span>Product: {p?.code ?? `#${row.product}`}</span>;
  }
  if (row.variant) {
    const v = (variants ?? []).find((r) => r.id === row.variant);
    return <span>Variant: {v?.sku ?? `#${row.variant}`}</span>;
  }
  return <span className="text-muted-foreground">—</span>;
}

const columns: ColumnDef<Barcode, unknown>[] = [
  { accessorKey: 'value', header: () => t('common.value') },
  { accessorKey: 'type', header: () => t('common.type') },
  {
    id: 'target',
    header: () => 'Target',
    cell: ({ row }) => <TargetCell row={row.original} />,
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
          {({ form, errorMap }) => {
            // Barcode belongs to exactly one of product or variant. Render a
            // small target toggle and show only the corresponding picker so
            // users can't accidentally set both and trip the XOR refine.
            const initialTarget: 'product' | 'variant' = initial.variant ? 'variant' : 'product';
            return (
              <BarcodeFormFields form={form} errorMap={errorMap} initialTarget={initialTarget} />
            );
          }}
        </CatalogFormBody>
      )}
    />
  );
}

interface BarcodeFormFieldsProps {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  form: any;
  errorMap: Record<string, unknown> | undefined;
  initialTarget: 'product' | 'variant';
}

function BarcodeFormFields({ form, errorMap, initialTarget }: BarcodeFormFieldsProps) {
  const [target, setTarget] = React.useState<'product' | 'variant'>(initialTarget);

  // Whenever the target switches, clear the field on the opposite side so the
  // XOR refine in `barcodeSchema` is satisfied.
  React.useEffect(() => {
    if (target === 'product') {
      form.setFieldValue('variant', null);
    } else {
      form.setFieldValue('product', null);
    }
  }, [target, form]);

  return (
    <>
      <form.Field name="value">
        {(f: never) => <Field field={f} label={t('common.value')} formErrorMap={errorMap} />}
      </form.Field>
      <form.Field name="type">
        {(f: never) => (
          <SelectField
            field={f}
            label={t('common.type')}
            options={TYPE_OPTS}
            formErrorMap={errorMap}
          />
        )}
      </form.Field>

      <div className="space-y-1.5">
        <div className="text-sm font-medium">Attach to</div>
        <div className="flex gap-4 text-sm">
          <label className="flex items-center gap-2">
            <input
              type="radio"
              name="bc-target"
              checked={target === 'product'}
              onChange={() => setTarget('product')}
            />
            <span>{t('common.product')}</span>
          </label>
          <label className="flex items-center gap-2">
            <input
              type="radio"
              name="bc-target"
              checked={target === 'variant'}
              onChange={() => setTarget('variant')}
            />
            <span>{t('common.variant')}</span>
          </label>
        </div>
      </div>

      {target === 'product' ? (
        <form.Field name="product">
          {(f: never) => (
            <ProductSelectField
              field={f}
              label={t('common.product')}
              allowEmpty={false}
              formErrorMap={errorMap}
            />
          )}
        </form.Field>
      ) : (
        <form.Field name="variant">
          {(f: never) => (
            <VariantSelectField
              field={f}
              label={t('common.variant')}
              allowEmpty={false}
              formErrorMap={errorMap}
            />
          )}
        </form.Field>
      )}
    </>
  );
}
