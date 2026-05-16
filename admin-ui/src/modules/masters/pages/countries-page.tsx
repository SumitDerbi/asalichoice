import type { ColumnDef } from '@tanstack/react-table';
import { Field } from '@/lib/forms';
import { MasterListPage } from '../components/master-list-page';
import { MasterFormBody } from '../components/master-form-body';
import { countrySchema, type CountryInput } from '../schemas';
import type { Country } from '../api/types';
import { t } from '../lib/i18n';

const columns: ColumnDef<Country, unknown>[] = [
  { accessorKey: 'iso2', header: () => t('countries.field.iso2') },
  { accessorKey: 'iso3', header: () => t('countries.field.iso3') },
  { accessorKey: 'name', header: () => t('common.name') },
  { accessorKey: 'phone_code', header: () => t('countries.field.phone_code') },
  { accessorKey: 'currency_code', header: () => t('countries.field.currency_code') },
];

const KNOWN = ['iso2', 'iso3', 'name', 'phone_code', 'currency_code'] as const;

export function CountriesPage() {
  return (
    <MasterListPage<Country, CountryInput>
      endpoint="countries"
      permissionDomain="country"
      title={t('countries.title')}
      searchField="search"
      columns={columns}
      renderForm={({ initial, onSubmit, onCancel, submitting }) => (
        <MasterFormBody<CountryInput>
          schema={countrySchema}
          defaultValues={{
            iso2: initial.iso2 ?? '',
            iso3: initial.iso3 ?? '',
            name: initial.name ?? '',
            phone_code: initial.phone_code ?? '',
            currency_code: initial.currency_code ?? '',
          }}
          knownFields={KNOWN}
          onSubmit={onSubmit}
          onCancel={onCancel}
          submitting={submitting}
        >
          {({ form, errorMap }) => (
            <>
              <form.Field name="iso2">
                {(f) => (
                  <Field field={f} label={t('countries.field.iso2')} formErrorMap={errorMap} />
                )}
              </form.Field>
              <form.Field name="iso3">
                {(f) => (
                  <Field field={f} label={t('countries.field.iso3')} formErrorMap={errorMap} />
                )}
              </form.Field>
              <form.Field name="name">
                {(f) => <Field field={f} label={t('common.name')} formErrorMap={errorMap} />}
              </form.Field>
              <form.Field name="phone_code">
                {(f) => (
                  <Field
                    field={f}
                    label={t('countries.field.phone_code')}
                    formErrorMap={errorMap}
                  />
                )}
              </form.Field>
              <form.Field name="currency_code">
                {(f) => (
                  <Field
                    field={f}
                    label={t('countries.field.currency_code')}
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
