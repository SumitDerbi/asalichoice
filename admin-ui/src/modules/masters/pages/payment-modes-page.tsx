import type { ColumnDef } from '@tanstack/react-table';
import { Field } from '@/lib/forms';
import { MasterListPage } from '../components/master-list-page';
import { MasterFormBody } from '../components/master-form-body';
import { SelectField } from '../components/select-field';
import { paymentModeSchema, type PaymentModeInput } from '../schemas';
import type { PaymentMode } from '../api/types';
import { t } from '../lib/i18n';

const columns: ColumnDef<PaymentMode, unknown>[] = [
  { accessorKey: 'code', header: () => t('common.code') },
  { accessorKey: 'name', header: () => t('common.name') },
  { accessorKey: 'type', header: () => t('payment_modes.field.type') },
];

const KIND_OPTIONS = [
  { value: 'CASH', label: 'Cash' },
  { value: 'UPI', label: 'UPI' },
  { value: 'CARD', label: 'Card' },
  { value: 'WALLET', label: 'Wallet' },
  { value: 'COD', label: 'COD' },
  { value: 'BANK', label: 'Bank transfer' },
];

const KNOWN = ['code', 'name', 'type', 'branches', 'config_json'] as const;

export function PaymentModesPage() {
  return (
    <MasterListPage<PaymentMode, PaymentModeInput>
      endpoint="payment-modes"
      permissionDomain="paymentmode"
      title={t('payment_modes.title')}
      searchField="search"
      columns={columns}
      renderForm={({ initial, onSubmit, onCancel, submitting }) => (
        <MasterFormBody<PaymentModeInput>
          schema={paymentModeSchema}
          defaultValues={{
            code: initial.code ?? '',
            name: initial.name ?? '',
            type: (initial.type as PaymentModeInput['type']) ?? 'CASH',
            branches: initial.branches ?? [],
            config_json: initial.config_json ?? {},
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
                    label={t('payment_modes.field.type')}
                    options={KIND_OPTIONS}
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
