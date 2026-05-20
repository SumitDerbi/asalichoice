import * as React from 'react';
import type { ColumnDef } from '@tanstack/react-table';
import { Field } from '@/lib/forms';
import { CatalogListPage } from '../components/catalog-list-page';
import { CatalogFormBody } from '../components/catalog-form-body';
import { RemoteSelectField } from '@/modules/masters/components/select-field';
import { ProductSelectField, VariantSelectField } from '../components/catalog-select-field';
import { useCanManagePrices } from '../lib/use-permission';
import { priceSchema, type PriceInput } from '../schemas';
import type { ProductPrice, Product, ProductVariant } from '../api/types';
import { useCatalogList } from '../api/hooks';
import { useMasterList } from '@/modules/masters/api/hooks';
import type { Branch } from '@/modules/masters/api/types';
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

function ProductCodeCell({ productId }: { productId: number | null }) {
  const { data } = useCatalogList<Product>('products');
  if (productId == null) return <span className="text-muted-foreground">—</span>;
  const p = (data ?? []).find((r) => r.id === productId);
  return <span>{p?.code ?? `#${productId}`}</span>;
}

function VariantCodeCell({ variantId }: { variantId: number | null }) {
  const { data } = useCatalogList<ProductVariant>('variants');
  if (variantId == null) return <span className="text-muted-foreground">—</span>;
  const v = (data ?? []).find((r) => r.id === variantId);
  return <span>{v?.sku ?? `#${variantId}`}</span>;
}

function BranchCodeCell({ branchId }: { branchId: number }) {
  const { data } = useMasterList<Branch>('branches');
  const b = (data ?? []).find((r) => r.id === branchId);
  return <span>{b?.code ?? `#${branchId}`}</span>;
}

const columns: ColumnDef<ProductPrice, unknown>[] = [
  {
    accessorKey: 'product',
    header: () => 'Product',
    cell: ({ row }) => <ProductCodeCell productId={row.original.product} />,
  },
  {
    accessorKey: 'variant',
    header: () => 'Variant',
    cell: ({ row }) => <VariantCodeCell variantId={row.original.variant} />,
  },
  {
    accessorKey: 'branch',
    header: () => t('common.branch'),
    cell: ({ row }) => <BranchCodeCell branchId={row.original.branch} />,
  },
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
              <PriceTargetFields
                form={form}
                errorMap={errorMap}
                initialTarget={initial.variant ? 'variant' : 'product'}
              />
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

interface PriceTargetFieldsProps {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  form: any;
  errorMap: Record<string, unknown> | undefined;
  initialTarget: 'product' | 'variant';
}

function PriceTargetFields({ form, errorMap, initialTarget }: PriceTargetFieldsProps) {
  const [target, setTarget] = React.useState<'product' | 'variant'>(initialTarget);

  // Clear the opposite side whenever the target toggle flips so the XOR
  // refine in `priceSchema` is satisfied.
  React.useEffect(() => {
    if (target === 'product') form.setFieldValue('variant', null);
    else form.setFieldValue('product', null);
  }, [target, form]);

  return (
    <>
      <div className="space-y-1.5">
        <div className="text-sm font-medium">Price for</div>
        <div className="flex gap-4 text-sm">
          <label className="flex items-center gap-2">
            <input
              type="radio"
              name="price-target"
              checked={target === 'product'}
              onChange={() => setTarget('product')}
            />
            <span>{t('common.product')}</span>
          </label>
          <label className="flex items-center gap-2">
            <input
              type="radio"
              name="price-target"
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
