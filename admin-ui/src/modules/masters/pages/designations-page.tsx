import type { ColumnDef } from '@tanstack/react-table';
import { Field } from '@/lib/forms';
import { MasterListPage } from '../components/master-list-page';
import { MasterFormBody } from '../components/master-form-body';
import { RemoteSelectField } from '../components/select-field';
import { designationSchema, type DesignationInput } from '../schemas';
import type { Designation } from '../api/types';
import { t } from '../lib/i18n';

const columns: ColumnDef<Designation, unknown>[] = [
  { accessorKey: 'code', header: () => t('common.code') },
  { accessorKey: 'name', header: () => t('common.name') },
];

const KNOWN = ['code', 'name', 'department'] as const;

export function DesignationsPage() {
  return (
    <MasterListPage<Designation, DesignationInput>
      endpoint="designations"
      permissionDomain="designation"
      title={t('designations.title')}
      searchField="search"
      columns={columns}
      renderForm={({ initial, onSubmit, onCancel, submitting }) => (
        <MasterFormBody<DesignationInput>
          schema={designationSchema}
          defaultValues={{
            code: initial.code ?? '',
            name: initial.name ?? '',
            department: initial.department ?? null,
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
              <form.Field name="department">
                {(f) => (
                  <RemoteSelectField
                    field={f}
                    label={t('designations.field.department')}
                    endpoint="departments"
                    getLabel={(d) => `${d.code} – ${d.name}`}
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
