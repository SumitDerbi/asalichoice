import type { ColumnDef } from '@tanstack/react-table';
import { Field } from '@/lib/forms';
import { MasterListPage } from '../components/master-list-page';
import { MasterFormBody } from '../components/master-form-body';
import { TextareaField } from '../components/select-field';
import { departmentSchema, type DepartmentInput } from '../schemas';
import type { Department } from '../api/types';
import { t } from '../lib/i18n';

const columns: ColumnDef<Department, unknown>[] = [
  { accessorKey: 'code', header: () => t('common.code') },
  { accessorKey: 'name', header: () => t('common.name') },
  { accessorKey: 'description', header: () => t('common.description') },
];

const KNOWN = ['code', 'name', 'description'] as const;

export function DepartmentsPage() {
  return (
    <MasterListPage<Department, DepartmentInput>
      endpoint="departments"
      permissionDomain="department"
      title={t('departments.title')}
      searchField="search"
      columns={columns}
      renderForm={({ initial, onSubmit, onCancel, submitting }) => (
        <MasterFormBody<DepartmentInput>
          schema={departmentSchema}
          defaultValues={{
            code: initial.code ?? '',
            name: initial.name ?? '',
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
