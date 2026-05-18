import * as React from 'react';
import { Field } from '@/lib/forms';
import { MasterFormBody } from '@/modules/masters/components/master-form-body';
import { TextareaField } from '@/modules/masters/components/select-field';
import { roleSchema, type RoleValues } from '../schemas';
import { usePermissionsList } from '../api/hooks';
import type { Role, Permission } from '../api/types';

interface RoleFormProps {
  initial: Partial<Role>;
  onSubmit: (values: RoleValues) => Promise<void>;
  onCancel: () => void;
  submitting: boolean;
}

const KNOWN = ['code', 'name', 'description', 'permission_ids'] as const;

function groupByModule(permissions: Permission[]): Record<string, Permission[]> {
  const out: Record<string, Permission[]> = {};
  for (const p of permissions) {
    (out[p.module] ??= []).push(p);
  }
  return out;
}

export function RoleForm({ initial, onSubmit, onCancel, submitting }: RoleFormProps) {
  const { data: permissions } = usePermissionsList();
  const grouped = React.useMemo(() => groupByModule(permissions ?? []), [permissions]);
  const isSystem = !!initial.is_system;

  return (
    <MasterFormBody<RoleValues>
      schema={roleSchema}
      defaultValues={{
        code: initial.code ?? '',
        name: initial.name ?? '',
        description: initial.description ?? '',
        permission_ids: initial.permission_ids ?? [],
      }}
      knownFields={KNOWN}
      onSubmit={onSubmit}
      onCancel={onCancel}
      submitting={submitting}
    >
      {({ form, errorMap }) => (
        <>
          {isSystem && (
            <p className="rounded border border-amber-300 bg-amber-50 px-2 py-1 text-xs text-amber-700">
              System role — code and permissions cannot be modified.
            </p>
          )}
          <form.Field name="code">
            {(f) => <Field field={f} label="Code" formErrorMap={errorMap} />}
          </form.Field>
          <form.Field name="name">
            {(f) => <Field field={f} label="Name" formErrorMap={errorMap} />}
          </form.Field>
          <form.Field name="description">
            {(f) => <TextareaField field={f} label="Description" formErrorMap={errorMap} />}
          </form.Field>
          <form.Field name="permission_ids">
            {(f) => {
              const ids = (f.state.value ?? []) as number[];
              const toggle = (pid: number, checked: boolean) => {
                const next = checked ? [...ids, pid] : ids.filter((x) => x !== pid);
                f.handleChange(next as never);
              };
              const toggleModule = (mod: string, checked: boolean) => {
                const modIds = (grouped[mod] ?? []).map((p) => p.id);
                const set = new Set(ids);
                if (checked) modIds.forEach((id) => set.add(id));
                else modIds.forEach((id) => set.delete(id));
                f.handleChange(Array.from(set) as never);
              };
              return (
                <div className="space-y-2">
                  <span className="text-sm font-medium">Permissions</span>
                  <div className="max-h-80 space-y-3 overflow-y-auto rounded border p-2">
                    {Object.keys(grouped)
                      .sort()
                      .map((mod) => {
                        const perms = grouped[mod];
                        const allChecked = perms.every((p) => ids.includes(p.id));
                        return (
                          <div key={mod} className="space-y-1">
                            <label className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                              <input
                                type="checkbox"
                                checked={allChecked}
                                disabled={isSystem}
                                onChange={(e) => toggleModule(mod, e.target.checked)}
                              />
                              {mod}
                            </label>
                            <div className="ml-5 grid grid-cols-1 gap-1 md:grid-cols-2">
                              {perms.map((p) => (
                                <label
                                  key={p.id}
                                  className="flex items-start gap-2 text-xs"
                                  title={p.description}
                                >
                                  <input
                                    type="checkbox"
                                    checked={ids.includes(p.id)}
                                    disabled={isSystem}
                                    onChange={(e) => toggle(p.id, e.target.checked)}
                                  />
                                  <span>
                                    <span className="font-mono">{p.code}</span>
                                    <span className="ml-1 text-muted-foreground">{p.name}</span>
                                  </span>
                                </label>
                              ))}
                            </div>
                          </div>
                        );
                      })}
                    {(!permissions || permissions.length === 0) && (
                      <p className="text-xs text-muted-foreground">No permissions defined yet.</p>
                    )}
                  </div>
                </div>
              );
            }}
          </form.Field>
        </>
      )}
    </MasterFormBody>
  );
}
