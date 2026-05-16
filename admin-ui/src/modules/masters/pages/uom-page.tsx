import type { ColumnDef } from '@tanstack/react-table';
import { Field } from '@/lib/forms';
import { MasterListPage } from '../components/master-list-page';
import { MasterFormBody } from '../components/master-form-body';
import { RemoteSelectField } from '../components/select-field';
import { uomSchema, type UomInput } from '../schemas';
import type { UnitOfMeasure } from '../api/types';
import { t } from '../lib/i18n';

const columns: ColumnDef<UnitOfMeasure, unknown>[] = [
  { accessorKey: 'code', header: () => t('common.code') },
  { accessorKey: 'name', header: () => t('common.name') },
  { accessorKey: 'symbol', header: () => t('uom.field.symbol') },
  { accessorKey: 'conversion_factor', header: () => t('uom.field.conversion_factor') },
];

const KNOWN = ['code', 'name', 'symbol', 'parent', 'conversion_factor'] as const;

export function UnitsOfMeasurePage() {
  return (
    <MasterListPage<UnitOfMeasure, UomInput>
      endpoint="uom"
      permissionDomain="uom"
      title={t('uom.title')}
      searchField="search"
      columns={columns}
      renderForm={({ initial, onSubmit, onCancel, submitting }) => (
        <MasterFormBody<UomInput>
          schema={uomSchema}
          defaultValues={{
            code: initial.code ?? '',
            name: initial.name ?? '',
            symbol: initial.symbol ?? '',
            parent: initial.parent ?? null,
            conversion_factor: initial.conversion_factor ?? '1',
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
              <form.Field name="symbol">
                {(f) => <Field field={f} label={t('uom.field.symbol')} formErrorMap={errorMap} />}
              </form.Field>
              <form.Field name="parent">
                {(f) => (
                  <RemoteSelectField
                    field={f}
                    label={t('uom.field.parent')}
                    endpoint="uom"
                    getLabel={(d) => `${d.code} – ${d.name}`}
                    formErrorMap={errorMap}
                  />
                )}
              </form.Field>
              <form.Field name="conversion_factor">
                {(f) => (
                  <Field
                    field={f}
                    label={t('uom.field.conversion_factor')}
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
