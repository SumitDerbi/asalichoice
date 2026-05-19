import type { ColumnDef } from '@tanstack/react-table';
import { Link } from 'react-router-dom';
import { toast } from 'sonner';
import { useQuery } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Field } from '@/lib/forms';
import { ApiError } from '@/lib/api/errors';
import { apiClient } from '@/lib/api/client';
import { useBranchStore } from '@/lib/branch/store';
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
import type { Product, ProductPrice } from '../api/types';
import { t } from '../lib/i18n';
import { ProductMediaTab } from '../components/product-media-tab';

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
  'seo_title',
  'seo_description',
  'seo_image',
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
      id: 'thumb',
      header: () => <span className="sr-only">Image</span>,
      cell: ({ row }) => {
        const src = row.original.images?.[0]?.image;
        if (!src) {
          return <div className="h-10 w-10 rounded border bg-muted/30" aria-hidden="true" />;
        }
        return (
          <img
            src={src}
            alt={row.original.images?.[0]?.alt || row.original.name}
            className="h-10 w-10 rounded border object-cover"
            loading="lazy"
          />
        );
      },
    },
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
      id: 'price_from',
      header: () => 'Price from',
      cell: ({ row }) => <PriceFromCell productId={row.original.id} />,
    },
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
            seo_title: initial.seo_title ?? '',
            seo_description: initial.seo_description ?? '',
            seo_image: initial.seo_image ?? null,
          }}
          knownFields={KNOWN}
          onSubmit={onSubmit}
          onCancel={onCancel}
          submitting={submitting}
        >
          {({ form, errorMap }) => (
            <Tabs defaultValue="basic" className="w-full">
              <TabsList className="w-full overflow-x-auto">
                <TabsTrigger value="basic">Basic</TabsTrigger>
                <TabsTrigger value="variants">Variants</TabsTrigger>
                <TabsTrigger value="media">Media</TabsTrigger>
                <TabsTrigger value="pricing">Pricing</TabsTrigger>
                <TabsTrigger value="availability">Availability</TabsTrigger>
                <TabsTrigger value="seo">SEO</TabsTrigger>
              </TabsList>

              <TabsContent value="basic" className="space-y-3">
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
              </TabsContent>

              <TabsContent value="variants">
                <RelatedTabHint
                  message="Variants are managed on the dedicated Variants page."
                  to="/catalog/variants"
                />
              </TabsContent>

              <TabsContent value="media">
                <ProductMediaTab productId={initial.id} />
              </TabsContent>

              <TabsContent value="pricing">
                <RelatedTabHint
                  message="Prices are managed on the dedicated Prices page."
                  to="/catalog/prices"
                />
              </TabsContent>

              <TabsContent value="availability">
                <RelatedTabHint
                  message="Branch availability is managed on the dedicated Availability page."
                  to="/catalog/availability"
                />
              </TabsContent>

              <TabsContent value="seo" className="space-y-3">
                <form.Field name="seo_title">
                  {(f) => <Field field={f} label="SEO Title" formErrorMap={errorMap} />}
                </form.Field>
                <form.Field name="seo_description">
                  {(f) => (
                    <TextareaField field={f} label="SEO Description" formErrorMap={errorMap} />
                  )}
                </form.Field>
                <form.Field name="seo_image">
                  {(f) => <Field field={f} label="SEO Image URL" formErrorMap={errorMap} />}
                </form.Field>
              </TabsContent>
            </Tabs>
          )}
        </CatalogFormBody>
      )}
    />
  );
}

function RelatedTabHint({ message, to }: { message: string; to: string }) {
  return (
    <div className="rounded-md border border-dashed bg-muted/40 p-4 text-sm text-muted-foreground">
      <p>{message}</p>
      <Link to={to} className="mt-2 inline-block font-medium text-primary hover:underline">
        Open page →
      </Link>
    </div>
  );
}

/**
 * Reads the lowest sale_price across all active price bands for a product
 * within the current branch. A single shared query is keyed by branch so
 * every row in the table reuses the same fetch (TanStack Query dedupes).
 */
function PriceFromCell({ productId }: { productId: number }) {
  const branchId = useBranchStore((s) => s.currentBranchId);
  const { data, isLoading } = useQuery<ProductPrice[]>({
    queryKey: ['catalog', 'prices', 'by-branch', branchId],
    queryFn: async () => {
      const res = await apiClient.get(`/catalog/prices/?branch=${branchId}`);
      return Array.isArray(res.data) ? res.data : (res.data.results ?? []);
    },
    enabled: branchId != null,
    staleTime: 30_000,
  });
  if (branchId == null) return <span className="text-xs text-muted-foreground">—</span>;
  if (isLoading) return <span className="text-xs text-muted-foreground">…</span>;
  const candidates = (data ?? []).filter((p) => p.product === productId && (p.is_active ?? true));
  if (candidates.length === 0) return <span className="text-xs text-muted-foreground">—</span>;
  const min = candidates.reduce<number | null>((acc, row) => {
    const n = Number(row.sale_price);
    if (Number.isNaN(n)) return acc;
    return acc == null || n < acc ? n : acc;
  }, null);
  if (min == null) return <span className="text-xs text-muted-foreground">—</span>;
  return <span className="font-mono text-sm">{min.toFixed(2)}</span>;
}
