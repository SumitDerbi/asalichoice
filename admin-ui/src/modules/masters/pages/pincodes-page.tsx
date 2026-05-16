import type { ColumnDef } from '@tanstack/react-table';
import { Field } from '@/lib/forms';
import { MasterListPage } from '../components/master-list-page';
import { MasterFormBody } from '../components/master-form-body';
import { RemoteSelectField } from '../components/select-field';
import { pincodeSchema, type PincodeInput } from '../schemas';
import type { Pincode } from '../api/types';
import { t } from '../lib/i18n';

const columns: ColumnDef<Pincode, unknown>[] = [
  { accessorKey: 'code', header: () => t('common.code') },
  { accessorKey: 'latitude', header: () => t('pincodes.field.latitude') },
  { accessorKey: 'longitude', header: () => t('pincodes.field.longitude') },
];

const KNOWN = ['code', 'city', 'latitude', 'longitude'] as const;

export function PincodesPage() {
  return (
    <MasterListPage<Pincode, PincodeInput>
      endpoint="pincodes"
      permissionDomain="pincode"
      title={t('pincodes.title')}
      searchField="search"
      columns={columns}
      renderForm={({ initial, onSubmit, onCancel, submitting }) => (
        <MasterFormBody<PincodeInput>
          schema={pincodeSchema}
          defaultValues={{
            code: initial.code ?? '',
            city: initial.city ?? null,
            latitude: initial.latitude ?? '',
            longitude: initial.longitude ?? '',
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
              <form.Field name="city">
                {(f) => (
                  <RemoteSelectField
                    field={f}
                    label={t('pincodes.field.city')}
                    endpoint="cities"
                    getLabel={(c) => c.name}
                    formErrorMap={errorMap}
                  />
                )}
              </form.Field>
              <form.Field name="latitude">
                {(f) => (
                  <Field field={f} label={t('pincodes.field.latitude')} formErrorMap={errorMap} />
                )}
              </form.Field>
              <form.Field name="longitude">
                {(f) => (
                  <Field field={f} label={t('pincodes.field.longitude')} formErrorMap={errorMap} />
                )}
              </form.Field>
            </>
          )}
        </MasterFormBody>
      )}
    />
  );
}
