import type { ColumnDef } from '@tanstack/react-table';
import { Field } from '@/lib/forms';
import { MasterListPage } from '../components/master-list-page';
import { MasterFormBody } from '../components/master-form-body';
import { RemoteSelectField, TextareaField } from '../components/select-field';
import { hsnSchema, type HsnInput } from '../schemas';
import type { HSNCode } from '../api/types';
import { t } from '../lib/i18n';

const columns: ColumnDef<HSNCode, unknown>[] = [
  { accessorKey: 'code', header: () => t('common.code') },
  { accessorKey: 'description', header: () => t('common.description') },
];

const KNOWN = ['code', 'description', 'default_tax'] as const;

export function HsnPage() {
  return (
    <MasterListPage<HSNCode, HsnInput>
      endpoint="hsn"
      permissionDomain="hsn"
      title={t('hsn.title')}
      searchField="search"
      columns={columns}
      renderForm={({ initial, onSubmit, onCancel, submitting }) => (
        <MasterFormBody<HsnInput>
          schema={hsnSchema}
          defaultValues={{
            code: initial.code ?? '',
            description: initial.description ?? '',
            default_tax: initial.default_tax ?? null,
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
              <form.Field name="description">
                {(f) => (
                  <TextareaField
                    field={f}
                    label={t('common.description')}
                    formErrorMap={errorMap}
                  />
                )}
              </form.Field>
              <form.Field name="default_tax">
                {(f) => (
                  <RemoteSelectField
                    field={f}
                    label={t('hsn.field.default_tax')}
                    endpoint="taxes"
                    getLabel={(taxRow) => `${taxRow.code} – ${taxRow.name}`}
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
