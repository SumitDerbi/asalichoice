import type { ColumnDef } from '@tanstack/react-table';
import { Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Field } from '@/lib/forms';
import { MasterListPage } from '../components/master-list-page';
import { MasterFormBody } from '../components/master-form-body';
import { RemoteSelectField } from '../components/select-field';
import { zoneSchema, type ZoneInput } from '../schemas';
import type { PincodeRange, Zone } from '../api/types';
import { t } from '../lib/i18n';

const columns: ColumnDef<Zone, unknown>[] = [
  { accessorKey: 'code', header: () => t('common.code') },
  { accessorKey: 'name', header: () => t('common.name') },
];

const KNOWN = ['code', 'name', 'branch', 'pincodes', 'pincode_ranges_json'] as const;

function RangeEditor({
  value,
  onChange,
}: {
  value: PincodeRange[];
  onChange: (next: PincodeRange[]) => void;
}) {
  const update = (idx: number, patch: Partial<PincodeRange>) => {
    onChange(value.map((r, i) => (i === idx ? { ...r, ...patch } : r)));
  };
  return (
    <div className="space-y-2">
      <span className="text-sm font-medium">{t('zones.field.pincode_ranges')}</span>
      {value.map((row, idx) => (
        <div key={idx} className="grid grid-cols-[1fr_1fr_auto] items-center gap-2">
          <Input
            placeholder="From"
            value={row.from}
            onChange={(e) => update(idx, { from: e.target.value })}
          />
          <Input
            placeholder="To"
            value={row.to}
            onChange={(e) => update(idx, { to: e.target.value })}
          />
          <Button
            type="button"
            variant="ghost"
            size="icon"
            onClick={() => onChange(value.filter((_, i) => i !== idx))}
            aria-label="Remove range"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      ))}
      <Button
        type="button"
        variant="outline"
        size="sm"
        onClick={() => onChange([...value, { from: '', to: '' }])}
      >
        Add range
      </Button>
    </div>
  );
}

export function ZonesPage() {
  return (
    <MasterListPage<Zone, ZoneInput>
      endpoint="zones"
      permissionDomain="zone"
      title={t('zones.title')}
      searchField="search"
      columns={columns}
      renderForm={({ initial, onSubmit, onCancel, submitting }) => (
        <MasterFormBody<ZoneInput>
          schema={zoneSchema}
          defaultValues={{
            code: initial.code ?? '',
            name: initial.name ?? '',
            branch: initial.branch ?? 0,
            pincodes: initial.pincodes ?? [],
            pincode_ranges_json: initial.pincode_ranges_json ?? [],
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
                    label={t('zones.field.branch')}
                    endpoint="branches"
                    getLabel={(b) => `${b.code} – ${b.name}`}
                    allowEmpty={false}
                    formErrorMap={errorMap}
                  />
                )}
              </form.Field>
              <form.Field name="pincode_ranges_json">
                {(f) => (
                  <RangeEditor
                    value={(f.state.value as PincodeRange[]) ?? []}
                    onChange={(next) => f.handleChange(next as never)}
                  />
                )}
              </form.Field>
              <form.Field name="pincodes">
                {(f) => {
                  const csv = ((f.state.value as number[]) ?? []).join(',');
                  return (
                    <div className="space-y-1.5">
                      <label className="text-sm font-medium">{t('zones.field.pincodes')}</label>
                      <Input
                        value={csv}
                        onChange={(e) => {
                          const ids = e.target.value
                            .split(',')
                            .map((s) => Number(s.trim()))
                            .filter((n) => Number.isFinite(n) && n > 0);
                          f.handleChange(ids as never);
                        }}
                        placeholder="1,2,3"
                      />
                    </div>
                  );
                }}
              </form.Field>
            </>
          )}
        </MasterFormBody>
      )}
    />
  );
}
