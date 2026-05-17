import type { ColumnDef } from '@tanstack/react-table';
import { Link } from 'react-router-dom';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Field } from '@/lib/forms';
import { ApiError } from '@/lib/api/errors';
import { CatalogListPage } from '../components/catalog-list-page';
import { CatalogFormBody } from '../components/catalog-form-body';
import {
  RemoteSelectField,
  SelectField,
  TextareaField,
} from '@/modules/masters/components/select-field';
import { useArchiveProduct } from '../api/hooks';
import { useCanManageCatalog } from '../lib/use-permission';
import { productSchema, type ProductInput } from '../schemas';
import type { Product } from '../api/types';
import { t } from '../lib/i18n';

const KNOWN = [
  'code',
  'sku',
  'slug',
  'name',
  'brand',
  'category',
  'hsn',
  'tax',
  'base_uom',
  'description',
  'status',
] as const;

const STATUS_OPTIONS = [
  { value: 'DRAFT', label: 'Draft' },
  { value: 'ACTIVE', label: 'Active' },
  { value: 'ARCHIVED', label: 'Archived' },
];

export function ProductsPage() {
  const canManage = useCanManageCatalog();
  const archiveMut = useArchiveProduct();

  const columns: ColumnDef<Product, unknown>[] = [
    {
      accessorKey: 'sku',
      header: () => t('common.sku'),
      cell: ({ row }) => (
        <Link className="font-medium text-primary hover:underline" to={`${row.original.id}`}>
          {row.original.sku}
        </Link>
      ),
    },
    { accessorKey: 'code', header: () => t('common.code') },
    { accessorKey: 'name', header: () => t('common.name') },
    {
      id: 'product_status',
      header: () => t('common.status'),
      cell: ({ row }) => {
        const s = row.original.status;
        const color =
          s === 'ACTIVE'
            ? 'bg-emerald-50 text-emerald-700'
            : s === 'ARCHIVED'
              ? 'bg-zinc-100 text-zinc-600'
              : 'bg-amber-50 text-amber-700';
        return <span className={`rounded px-1.5 py-0.5 text-xs ${color}`}>{s}</span>;
      },
    },
  ];

  return (
    <CatalogListPage<Product, ProductInput>
      endpoint="products"
      title={t('products.title')}
      canManage={canManage}
      searchField="q"
      filters={[
        {
          label: t('common.status'),
          param: 'status',
          options: STATUS_OPTIONS,
        },
      ]}
      columns={columns}
      hideStatus
      extraActions={(row) =>
        row.status !== 'ARCHIVED' ? (
          <Button
            size="sm"
            variant="ghost"
            disabled={!canManage}
            onClick={async () => {
              try {
                await archiveMut.mutateAsync(row.id);
                toast.success('Product archived.');
              } catch (err) {
                toast.error(err instanceof ApiError ? err.message : 'Archive failed.');
              }
            }}
          >
            {t('common.archive')}
          </Button>
        ) : null
      }
      renderForm={({ initial, onSubmit, onCancel, submitting }) => (
        <CatalogFormBody<ProductInput>
          schema={productSchema}
          defaultValues={{
            code: initial.code ?? '',
            sku: initial.sku ?? '',
            slug: initial.slug ?? '',
            name: initial.name ?? '',
            brand: initial.brand ?? null,
            category: (initial.category ?? 0) as number,
            hsn: initial.hsn ?? null,
            tax: initial.tax ?? null,
            base_uom: (initial.base_uom ?? 0) as number,
            description: initial.description ?? '',
            status: initial.status ?? 'DRAFT',
          }}
          knownFields={KNOWN}
          onSubmit={onSubmit}
          onCancel={onCancel}
          submitting={submitting}
        >
          {({ form, errorMap }) => (
            <>
              <form.Field name="code">
                {(f) => <Field field={f} label={t('common.code')} formErrorMap={errorMap} />}
              </form.Field>
              <form.Field name="sku">
                {(f) => <Field field={f} label={t('common.sku')} formErrorMap={errorMap} />}
              </form.Field>
              <form.Field name="slug">
                {(f) => <Field field={f} label={t('common.slug')} formErrorMap={errorMap} />}
              </form.Field>
              <form.Field name="name">
                {(f) => <Field field={f} label={t('common.name')} formErrorMap={errorMap} />}
              </form.Field>
              <form.Field name="category">
                {(f) => (
                  <RemoteSelectField
                    field={f}
                    label={t('common.category')}
                    endpoint="categories"
                    getLabel={(r) => `${r.code} — ${r.name}`}
                    allowEmpty={false}
                    formErrorMap={errorMap}
                  />
                )}
              </form.Field>
              <form.Field name="base_uom">
                {(f) => (
                  <RemoteSelectField
                    field={f}
                    label={t('common.base_uom')}
                    endpoint="uom"
                    getLabel={(r) => `${r.code} — ${r.name}`}
                    allowEmpty={false}
                    formErrorMap={errorMap}
                  />
                )}
              </form.Field>
              <form.Field name="brand">
                {(f) => (
                  <RemoteSelectField
                    field={f}
                    label={t('common.brand')}
                    endpoint="brands"
                    getLabel={(r) => `${r.code} — ${r.name}`}
                    allowEmpty
                    formErrorMap={errorMap}
                  />
                )}
              </form.Field>
              <form.Field name="status">
                {(f) => (
                  <SelectField
                    field={f}
                    label={t('common.status')}
                    options={STATUS_OPTIONS}
                    formErrorMap={errorMap}
                  />
                )}
              </form.Field>
              <form.Field name="description">
                {(f) => (
                  <TextareaField
                    field={f}
                    label={t('common.description')}
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
