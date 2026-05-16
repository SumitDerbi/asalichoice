import type { ColumnDef } from '@tanstack/react-table';
import { Field } from '@/lib/forms';
import { MasterListPage } from '../components/master-list-page';
import { MasterFormBody } from '../components/master-form-body';
import { RemoteSelectField, TextareaField } from '../components/select-field';
import { warehouseSchema, type WarehouseInput } from '../schemas';
import type { Warehouse } from '../api/types';
import { t } from '../lib/i18n';

const columns: ColumnDef<Warehouse, unknown>[] = [
  { accessorKey: 'code', header: () => t('common.code') },
  { accessorKey: 'name', header: () => t('common.name') },
];

const KNOWN = ['code', 'name', 'branch', 'address'] as const;

export function WarehousesPage() {
  return (
    <MasterListPage<Warehouse, WarehouseInput>
      endpoint="warehouses"
      permissionDomain="warehouse"
      title={t('warehouses.title')}
      searchField="search"
      columns={columns}
      renderForm={({ initial, onSubmit, onCancel, submitting }) => (
        <MasterFormBody<WarehouseInput>
          schema={warehouseSchema}
          defaultValues={{
            code: initial.code ?? '',
            name: initial.name ?? '',
            branch: initial.branch ?? 0,
            address: initial.address ?? '',
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
              <form.Field name="branch">
                {(f) => (
                  <RemoteSelectField
                    field={f}
                    label={t('warehouses.field.branch')}
                    endpoint="branches"
                    getLabel={(b) => `${b.code} – ${b.name}`}
                    allowEmpty={false}
                    formErrorMap={errorMap}
                  />
                )}
              </form.Field>
              <form.Field name="address">
                {(f) => (
                  <TextareaField
                    field={f}
                    label={t('warehouses.field.address')}
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
