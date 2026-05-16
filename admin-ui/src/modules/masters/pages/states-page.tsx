import type { ColumnDef } from '@tanstack/react-table';
import { Field } from '@/lib/forms';
import { MasterListPage } from '../components/master-list-page';
import { MasterFormBody } from '../components/master-form-body';
import { RemoteSelectField } from '../components/select-field';
import { stateSchema, type StateInput } from '../schemas';
import type { State } from '../api/types';
import { t } from '../lib/i18n';

const columns: ColumnDef<State, unknown>[] = [
  { accessorKey: 'code', header: () => t('common.code') },
  { accessorKey: 'name', header: () => t('common.name') },
  { accessorKey: 'gst_state_code', header: () => t('states.field.gst_state_code') },
];

const KNOWN = ['code', 'name', 'country', 'gst_state_code'] as const;

export function StatesPage() {
  return (
    <MasterListPage<State, StateInput>
      endpoint="states"
      permissionDomain="state"
      title={t('states.title')}
      searchField="search"
      columns={columns}
      renderForm={({ initial, onSubmit, onCancel, submitting }) => (
        <MasterFormBody<StateInput>
          schema={stateSchema}
          defaultValues={{
            country: initial.country ?? 0,
            code: initial.code ?? '',
            name: initial.name ?? '',
            gst_state_code: initial.gst_state_code ?? '',
          }}
          knownFields={KNOWN}
          onSubmit={onSubmit}
          onCancel={onCancel}
          submitting={submitting}
        >
          {({ form, errorMap }) => (
            <>
              <form.Field name="country">
                {(f) => (
                  <RemoteSelectField
                    field={f}
                    label={t('states.field.country')}
                    endpoint="countries"
                    getLabel={(c) => `${c.iso2} – ${c.name}`}
                    allowEmpty={false}
                    formErrorMap={errorMap}
                  />
                )}
              </form.Field>
              <form.Field name="code">
                {(f) => <Field field={f} label={t('common.code')} formErrorMap={errorMap} />}
              </form.Field>
              <form.Field name="name">
                {(f) => <Field field={f} label={t('common.name')} formErrorMap={errorMap} />}
              </form.Field>
              <form.Field name="gst_state_code">
                {(f) => (
                  <Field
                    field={f}
                    label={t('states.field.gst_state_code')}
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
