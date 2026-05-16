import type { ColumnDef } from '@tanstack/react-table';
import { Field } from '@/lib/forms';
import { MasterListPage } from '../components/master-list-page';
import { MasterFormBody } from '../components/master-form-body';
import { RemoteSelectField, TextareaField } from '../components/select-field';
import { categorySchema, type CategoryInput } from '../schemas';
import type { Category } from '../api/types';
import { t } from '../lib/i18n';

const columns: ColumnDef<Category, unknown>[] = [
  { accessorKey: 'code', header: () => t('common.code') },
  { accessorKey: 'name', header: () => t('common.name') },
  { accessorKey: 'seo_slug', header: () => t('categories.field.seo_slug') },
];

const KNOWN = ['code', 'name', 'parent', 'seo_slug', 'description'] as const;

export function CategoriesPage() {
  return (
    <MasterListPage<Category, CategoryInput>
      endpoint="categories"
      permissionDomain="category"
      title={t('categories.title')}
      searchField="search"
      columns={columns}
      renderForm={({ initial, onSubmit, onCancel, submitting }) => (
        <MasterFormBody<CategoryInput>
          schema={categorySchema}
          defaultValues={{
            code: initial.code ?? '',
            name: initial.name ?? '',
            parent: initial.parent ?? null,
            seo_slug: initial.seo_slug ?? '',
            description: initial.description ?? '',
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
              <form.Field name="parent">
                {(f) => (
                  <RemoteSelectField
                    field={f}
                    label={t('categories.field.parent')}
                    endpoint="categories"
                    getLabel={(c) => `${c.code} – ${c.name}`}
                    formErrorMap={errorMap}
                  />
                )}
              </form.Field>
              <form.Field name="seo_slug">
                {(f) => (
                  <Field field={f} label={t('categories.field.seo_slug')} formErrorMap={errorMap} />
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
        </MasterFormBody>
      )}
    />
  );
}
