import type { ColumnDef } from '@tanstack/react-table';
import { Field } from '@/lib/forms';
import { MasterListPage } from '../components/master-list-page';
import { MasterFormBody } from '../components/master-form-body';
import { RemoteSelectField } from '../components/select-field';
import { citySchema, type CityInput } from '../schemas';
import type { City } from '../api/types';
import { t } from '../lib/i18n';

const columns: ColumnDef<City, unknown>[] = [
  { accessorKey: 'name', header: () => t('common.name') },
];

const KNOWN = ['name', 'state'] as const;

export function CitiesPage() {
  return (
    <MasterListPage<City, CityInput>
      endpoint="cities"
      permissionDomain="city"
      title={t('cities.title')}
      searchField="search"
      columns={columns}
      renderForm={({ initial, onSubmit, onCancel, submitting }) => (
        <MasterFormBody<CityInput>
          schema={citySchema}
          defaultValues={{
            state: initial.state ?? 0,
            name: initial.name ?? '',
          }}
          knownFields={KNOWN}
          onSubmit={onSubmit}
          onCancel={onCancel}
          submitting={submitting}
        >
          {({ form, errorMap }) => (
            <>
              <form.Field name="state">
                {(f) => (
                  <RemoteSelectField
                    field={f}
                    label={t('cities.field.state')}
                    endpoint="states"
                    getLabel={(s) => `${s.code} – ${s.name}`}
                    allowEmpty={false}
                    formErrorMap={errorMap}
                  />
                )}
              </form.Field>
              <form.Field name="name">
                {(f) => <Field field={f} label={t('common.name')} formErrorMap={errorMap} />}
              </form.Field>
            </>
          )}
        </MasterFormBody>
      )}
    />
  );
}
