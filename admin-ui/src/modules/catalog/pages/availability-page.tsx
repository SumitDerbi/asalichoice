import type { ColumnDef } from '@tanstack/react-table';
import { CatalogListPage } from '../components/catalog-list-page';
import { CatalogFormBody } from '../components/catalog-form-body';
import { RemoteSelectField } from '@/modules/masters/components/select-field';
import { ProductSelectField } from '../components/catalog-select-field';
import { CheckboxField } from '../components/json-field';
import { useCanManageCatalog } from '../lib/use-permission';
import { availabilitySchema, type AvailabilityInput } from '../schemas';
import type { ProductBranchAvailability, Product } from '../api/types';
import { useCatalogList } from '../api/hooks';
import { useMasterList } from '@/modules/masters/api/hooks';
import type { Branch } from '@/modules/masters/api/types';
import { t } from '../lib/i18n';

const KNOWN = ['product', 'branch', 'is_listed'] as const;

function ProductCodeCell({ productId }: { productId: number }) {
  const { data } = useCatalogList<Product>('products');
  const p = (data ?? []).find((r) => r.id === productId);
  if (!p) return <span className="text-muted-foreground">#{productId}</span>;
  return <span>{p.code}</span>;
}

function BranchCodeCell({ branchId }: { branchId: number }) {
  const { data } = useMasterList<Branch>('branches');
  const b = (data ?? []).find((r) => r.id === branchId);
  if (!b) return <span className="text-muted-foreground">#{branchId}</span>;
  return <span>{b.code}</span>;
}

const columns: ColumnDef<ProductBranchAvailability, unknown>[] = [
  {
    accessorKey: 'product',
    header: () => t('common.product'),
    cell: ({ row }) => <ProductCodeCell productId={row.original.product} />,
  },
  {
    accessorKey: 'branch',
    header: () => t('common.branch'),
    cell: ({ row }) => <BranchCodeCell branchId={row.original.branch} />,
  },
  {
    id: 'is_listed',
    header: () => t('common.is_listed'),
    cell: ({ row }) => (row.original.is_listed ? '✓' : '—'),
  },
];

export function AvailabilityPage() {
  const canManage = useCanManageCatalog();
  return (
    <CatalogListPage<ProductBranchAvailability, AvailabilityInput>
      endpoint="availability"
      title={t('availability.title')}
      subtitle={t('availability.subtitle')}
      canManage={canManage}
      searchField={null}
      columns={columns}
      renderForm={({ initial, onSubmit, onCancel, submitting }) => (
        <CatalogFormBody<AvailabilityInput>
          schema={availabilitySchema}
          defaultValues={{
            product: (initial.product ?? null) as unknown as number,
            branch: (initial.branch ?? null) as unknown as number,
            is_listed: initial.is_listed ?? true,
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
                  <ProductSelectField
                    field={f}
                    label={t('common.product')}
                    allowEmpty={false}
                    formErrorMap={errorMap}
                  />
                )}
              </form.Field>
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
              <form.Field name="is_listed">
                {(f) => (
                  <CheckboxField field={f} label={t('common.is_listed')} formErrorMap={errorMap} />
                )}
              </form.Field>
            </>
          )}
        </CatalogFormBody>
      )}
    />
  );
}
