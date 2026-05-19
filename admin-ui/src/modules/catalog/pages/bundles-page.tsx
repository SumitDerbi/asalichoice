import type { ColumnDef } from '@tanstack/react-table';
import { Field } from '@/lib/forms';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { CatalogListPage } from '../components/catalog-list-page';
import { CatalogFormBody } from '../components/catalog-form-body';
import { SelectField } from '@/modules/masters/components/select-field';
import { BundleComponentsTab } from '../components/bundle-components-tab';
import { useCanManageCatalog } from '../lib/use-permission';
import { bundleSchema, type BundleInput } from '../schemas';
import type { Bundle } from '../api/types';
import { t } from '../lib/i18n';

const KNOWN = ['code', 'name', 'kind', 'price_policy', 'fixed_price'] as const;

const KIND_OPTS = [
  { value: 'COMBO', label: 'Combo' },
  { value: 'MIX_AND_MATCH', label: 'Mix & match' },
];

const POLICY_OPTS = [
  { value: 'SUM', label: 'Sum of components' },
  { value: 'FIXED', label: 'Fixed price' },
];

const columns: ColumnDef<Bundle, unknown>[] = [
  { accessorKey: 'code', header: () => t('common.code') },
  { accessorKey: 'name', header: () => t('common.name') },
  { accessorKey: 'kind', header: () => t('common.kind') },
  { accessorKey: 'price_policy', header: () => t('common.price_policy') },
  { accessorKey: 'fixed_price', header: () => t('common.fixed_price') },
];

export function BundlesPage() {
  const canManage = useCanManageCatalog();
  return (
    <CatalogListPage<Bundle, BundleInput>
      endpoint="bundles"
      title={t('bundles.title')}
      canManage={canManage}
      searchField="search"
      columns={columns}
      renderForm={({ initial, onSubmit, onCancel, submitting }) => (
        <CatalogFormBody<BundleInput>
          schema={bundleSchema}
          defaultValues={{
            code: initial.code ?? '',
            name: initial.name ?? '',
            kind: initial.kind ?? 'COMBO',
            price_policy: initial.price_policy ?? 'SUM',
            fixed_price: initial.fixed_price ?? null,
          }}
          knownFields={KNOWN}
          onSubmit={onSubmit}
          onCancel={onCancel}
          submitting={submitting}
        >
          {({ form, errorMap }) => (
            <Tabs defaultValue="basic" className="space-y-4">
              <TabsList>
                <TabsTrigger value="basic">Basic</TabsTrigger>
                <TabsTrigger value="components">Components</TabsTrigger>
              </TabsList>
              <TabsContent value="basic" className="space-y-3">
                <form.Field name="code">
                  {(f) => <Field field={f} label={t('common.code')} formErrorMap={errorMap} />}
                </form.Field>
                <form.Field name="name">
                  {(f) => <Field field={f} label={t('common.name')} formErrorMap={errorMap} />}
                </form.Field>
                <form.Field name="kind">
                  {(f) => (
                    <SelectField
                      field={f}
                      label={t('common.kind')}
                      options={KIND_OPTS}
                      formErrorMap={errorMap}
                    />
                  )}
                </form.Field>
                <form.Field name="price_policy">
                  {(f) => (
                    <SelectField
                      field={f}
                      label={t('common.price_policy')}
                      options={POLICY_OPTS}
                      formErrorMap={errorMap}
                    />
                  )}
                </form.Field>
                <form.Field name="fixed_price">
                  {(f) => (
                    <Field field={f} label={t('common.fixed_price')} formErrorMap={errorMap} />
                  )}
                </form.Field>
              </TabsContent>
              <TabsContent value="components">
                <BundleComponentsTab bundleId={initial.id} />
              </TabsContent>
            </Tabs>
          )}
        </CatalogFormBody>
      )}
    />
  );
}
