import type { ColumnDef } from '@tanstack/react-table';
import { Field } from '@/lib/forms';
import { CatalogListPage } from '../components/catalog-list-page';
import { CatalogFormBody } from '../components/catalog-form-body';
import { SelectField } from '@/modules/masters/components/select-field';
import { JsonField } from '../components/json-field';
import { useCanManageCatalog } from '../lib/use-permission';
import { attributeSchema, type AttributeInput } from '../schemas';
import type { Attribute } from '../api/types';
import { t } from '../lib/i18n';

const KNOWN = ['code', 'name', 'type', 'options_json'] as const;

const TYPE_OPTS = [
  { value: 'TEXT', label: 'Text' },
  { value: 'NUMBER', label: 'Number' },
  { value: 'BOOL', label: 'Boolean' },
  { value: 'SELECT', label: 'Select' },
];

const columns: ColumnDef<Attribute, unknown>[] = [
  { accessorKey: 'code', header: () => t('common.code') },
  { accessorKey: 'name', header: () => t('common.name') },
  { accessorKey: 'type', header: () => t('common.type') },
  {
    id: 'options',
    header: () => t('common.options_json'),
    cell: ({ row }) => {
      const opts = row.original.options_json;
      if (Array.isArray(opts) && opts.length > 0) return opts.join(', ');
      return '—';
    },
  },
];

export function AttributesPage() {
  const canManage = useCanManageCatalog();
  return (
    <CatalogListPage<Attribute, AttributeInput>
      endpoint="attributes"
      title={t('attributes.title')}
      subtitle={t('attributes.subtitle')}
      canManage={canManage}
      searchField="search"
      columns={columns}
      renderForm={({ initial, onSubmit, onCancel, submitting }) => (
        <CatalogFormBody<AttributeInput>
          schema={attributeSchema}
          defaultValues={{
            code: initial.code ?? '',
            name: initial.name ?? '',
            type: initial.type ?? 'TEXT',
            options_json: initial.options_json ?? [],
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
              <form.Field name="name">
                {(f) => <Field field={f} label={t('common.name')} formErrorMap={errorMap} />}
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
              <form.Field name="options_json">
                {(f) => (
                  <JsonField
                    field={f}
                    label={t('common.options_json')}
                    rows={4}
                    placeholder={'["Small", "Medium", "Large"]'}
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
