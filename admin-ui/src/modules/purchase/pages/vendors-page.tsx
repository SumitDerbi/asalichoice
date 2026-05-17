import * as React from 'react';
import { toast } from 'sonner';
import type { ColumnDef } from '@tanstack/react-table';
import { Button } from '@/components/ui/button';
import { Field } from '@/lib/forms';
import { ApiError } from '@/lib/api/errors';
import { Drawer } from '@/components/shared/drawer';
import { CatalogFormBody } from '@/modules/catalog/components/catalog-form-body';
import { PurchaseListPage, StatusBadge } from '../components/purchase-list-page';
import { usePurchaseAction, usePurchaseCreate, usePurchaseUpdate } from '../api/hooks';
import { useCanManageVendors } from '../lib/use-permission';
import { vendorSchema, type VendorInput } from '../schemas';
import type { Vendor } from '../api/types';
import { t } from '../lib/i18n';

const KNOWN = [
  'code',
  'name',
  'contact_name',
  'contact_email',
  'contact_mobile',
  'gstin',
  'pan',
  'credit_limit',
] as const;

interface FormProps {
  initial: Partial<Vendor>;
  onClose: () => void;
}

function VendorForm({ initial, onClose }: FormProps) {
  const createMut = usePurchaseCreate<Vendor, VendorInput>('vendors');
  const updateMut = usePurchaseUpdate<Vendor, VendorInput>('vendors');
  const submitting = createMut.isPending || updateMut.isPending;

  return (
    <CatalogFormBody<VendorInput>
      schema={vendorSchema}
      defaultValues={{
        code: initial.code ?? '',
        name: initial.name ?? '',
        contact_name: initial.contact_name ?? '',
        contact_email: initial.contact_email ?? '',
        contact_mobile: initial.contact_mobile ?? '',
        gstin: initial.gstin ?? '',
        pan: initial.pan ?? '',
        credit_limit: initial.credit_limit ?? '0',
      }}
      knownFields={KNOWN}
      onCancel={onClose}
      submitting={submitting}
      onSubmit={async (values) => {
        try {
          if (initial.id) {
            await updateMut.mutateAsync({ id: initial.id, values });
            toast.success('Vendor updated.');
          } else {
            await createMut.mutateAsync(values);
            toast.success('Vendor created.');
          }
          onClose();
        } catch (err) {
          toast.error(err instanceof ApiError ? err.message : 'Save failed.');
          throw err;
        }
      }}
    >
      {({ form, errorMap }) => (
        <>
          <form.Field name="code">
            {(f) => <Field field={f} label={t('common.code')} formErrorMap={errorMap} />}
          </form.Field>
          <form.Field name="name">
            {(f) => <Field field={f} label={t('common.name')} formErrorMap={errorMap} />}
          </form.Field>
          <form.Field name="contact_name">
            {(f) => <Field field={f} label="Contact" formErrorMap={errorMap} />}
          </form.Field>
          <form.Field name="contact_email">
            {(f) => <Field field={f} label={t('common.email')} formErrorMap={errorMap} />}
          </form.Field>
          <form.Field name="contact_mobile">
            {(f) => <Field field={f} label={t('common.mobile')} formErrorMap={errorMap} />}
          </form.Field>
          <form.Field name="gstin">
            {(f) => <Field field={f} label={t('common.gstin')} formErrorMap={errorMap} />}
          </form.Field>
          <form.Field name="pan">
            {(f) => <Field field={f} label={t('common.pan')} formErrorMap={errorMap} />}
          </form.Field>
          <form.Field name="credit_limit">
            {(f) => <Field field={f} label="Credit limit" formErrorMap={errorMap} />}
          </form.Field>
        </>
      )}
    </CatalogFormBody>
  );
}

export function VendorsPage() {
  const canManage = useCanManageVendors();
  const deactivateMut = usePurchaseAction<Vendor>('vendors', 'deactivate');
  const [editing, setEditing] = React.useState<Vendor | null>(null);

  const columns: ColumnDef<Vendor, unknown>[] = [
    { accessorKey: 'code', header: () => t('common.code') },
    { accessorKey: 'name', header: () => t('common.name') },
    { accessorKey: 'gstin', header: () => t('common.gstin') },
    { accessorKey: 'contact_mobile', header: () => t('common.mobile') },
    {
      id: 'status',
      header: () => t('common.status'),
      cell: ({ row }) => <StatusBadge value={row.original.is_active ? 'ACTIVE' : 'INACTIVE'} />,
    },
    {
      id: 'actions',
      header: () => <span className="sr-only">{t('common.actions')}</span>,
      cell: ({ row }) => (
        <div className="flex justify-end gap-2">
          <Button
            size="sm"
            variant="ghost"
            disabled={!canManage}
            onClick={() => setEditing(row.original)}
          >
            {t('common.edit')}
          </Button>
          {row.original.is_active && (
            <Button
              size="sm"
              variant="ghost"
              disabled={!canManage}
              onClick={async () => {
                try {
                  await deactivateMut.mutateAsync({ id: row.original.id });
                  toast.success('Vendor deactivated.');
                } catch (err) {
                  toast.error(err instanceof ApiError ? err.message : 'Failed.');
                }
              }}
            >
              {t('actions.deactivate')}
            </Button>
          )}
        </div>
      ),
    },
  ];

  return (
    <>
      <PurchaseListPage<Vendor>
        endpoint="vendors"
        title={t('vendors.title')}
        searchField="q"
        canCreate={canManage}
        columns={columns}
        renderCreate={(close) => <VendorForm initial={{}} onClose={close} />}
      />
      {editing && (
        <Drawer
          open
          onOpenChange={(o: boolean) => (o ? null : setEditing(null))}
          title={t('common.edit')}
        >
          <VendorForm initial={editing} onClose={() => setEditing(null)} />
        </Drawer>
      )}
    </>
  );
}
