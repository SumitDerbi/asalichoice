import type { ColumnDef } from '@tanstack/react-table';
import { Field } from '@/lib/forms';
import { MasterListPage } from '../components/master-list-page';
import { MasterFormBody } from '../components/master-form-body';
import { RemoteSelectField, SelectField, TextareaField } from '../components/select-field';
import { branchSchema, type BranchInput } from '../schemas';
import type { Branch } from '../api/types';
import { t } from '../lib/i18n';

const columns: ColumnDef<Branch, unknown>[] = [
  { accessorKey: 'code', header: () => t('common.code') },
  { accessorKey: 'name', header: () => t('common.name') },
  { accessorKey: 'type', header: () => t('branches.field.type') },
  { accessorKey: 'phone', header: () => t('branches.field.phone') },
];

const TYPE_OPTIONS = [
  { value: 'HQ', label: 'HQ' },
  { value: 'STORE', label: 'Store' },
  { value: 'WAREHOUSE', label: 'Warehouse' },
  { value: 'DARK_STORE', label: 'Dark store' },
] as const;

const KNOWN = [
  'code',
  'name',
  'type',
  'parent',
  'address',
  'phone',
  'email',
  'feature_flags_json',
] as const;

export function BranchesPage() {
  return (
    <MasterListPage<Branch, BranchInput>
      endpoint="branches"
      permissionDomain="branch"
      title={t('branches.title')}
      subtitle={t('branches.subtitle')}
      searchField="search"
      columns={columns}
      renderForm={({ initial, onSubmit, onCancel, submitting }) => (
        <MasterFormBody<BranchInput>
          schema={branchSchema}
          defaultValues={{
            code: initial.code ?? '',
            name: initial.name ?? '',
            type: (initial.type as BranchInput['type']) ?? 'STORE',
            parent: initial.parent ?? null,
            address: initial.address ?? '',
            phone: initial.phone ?? '',
            email: initial.email ?? '',
            feature_flags_json: initial.feature_flags_json ?? {},
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
                  <SelectField<string>
                    field={f}
                    label={t('branches.field.type')}
                    options={TYPE_OPTIONS as unknown as Array<{ value: string; label: string }>}
                    formErrorMap={errorMap}
                  />
                )}
              </form.Field>
              <form.Field name="parent">
                {(f) => (
                  <RemoteSelectField
                    field={f}
                    label={t('branches.field.parent')}
                    endpoint="branches"
                    getLabel={(b) => `${b.code} – ${b.name}`}
                    formErrorMap={errorMap}
                  />
                )}
              </form.Field>
              <form.Field name="phone">
                {(f) => (
                  <Field field={f} label={t('branches.field.phone')} formErrorMap={errorMap} />
                )}
              </form.Field>
              <form.Field name="email">
                {(f) => (
                  <Field
                    field={f}
                    type="email"
                    label={t('branches.field.email')}
                    formErrorMap={errorMap}
                  />
                )}
              </form.Field>
              <form.Field name="address">
                {(f) => (
                  <TextareaField
                    field={f}
                    label={t('branches.field.address')}
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
