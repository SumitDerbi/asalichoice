import { toast } from 'sonner';
import { Field } from '@/lib/forms';
import { Button } from '@/components/ui/button';
import { ApiError } from '@/lib/api/errors';
import { MasterFormBody } from '@/modules/masters/components/master-form-body';
import { userSchema, type UserValues } from '../schemas';
import { useRolesList, useUserResendInvite } from '../api/hooks';
import type { User, PrimaryIdentifier } from '../api/types';
import { BranchAccessSection } from './branch-access-section';

interface UserFormProps {
  initial: Partial<User>;
  onSubmit: (values: UserValues) => Promise<void>;
  onCancel: () => void;
  submitting: boolean;
}

const KNOWN = [
  'email',
  'mobile',
  'employee_code',
  'name',
  'primary_identifier',
  'is_staff',
  'is_active',
  'password',
  'role_ids',
] as const;

const IDENTIFIER_OPTIONS: Array<{ value: PrimaryIdentifier; label: string }> = [
  { value: 'EMAIL', label: 'Email' },
  { value: 'MOBILE', label: 'Mobile' },
  { value: 'EMP_CODE', label: 'Employee code' },
];

export function UserForm({ initial, onSubmit, onCancel, submitting }: UserFormProps) {
  const { data: roles } = useRolesList();
  const isEditing = !!initial.id;
  const resendInviteMut = useUserResendInvite();

  return (
    <MasterFormBody<UserValues>
      schema={userSchema}
      defaultValues={{
        email: initial.email ?? '',
        mobile: initial.mobile ?? '',
        employee_code: initial.employee_code ?? '',
        name: initial.name ?? '',
        primary_identifier: initial.primary_identifier ?? 'EMAIL',
        is_staff: initial.is_staff ?? false,
        is_active: initial.is_active ?? true,
        password: '',
        role_ids: (initial.roles ?? []).map((r) => r.id),
      }}
      knownFields={KNOWN}
      onSubmit={async (values) => {
        // Strip empty optionals so backend treats them as omitted.
        const payload = { ...values };
        if (!payload.password) delete payload.password;
        if (payload.mobile === '') payload.mobile = null;
        if (payload.employee_code === '') payload.employee_code = null;
        await onSubmit(payload);
      }}
      onCancel={onCancel}
      submitting={submitting}
      extraActions={
        isEditing && initial.id && initial.is_active === false ? (
          <Button
            size="sm"
            variant="outline"
            onClick={async () => {
              try {
                await resendInviteMut.mutateAsync(initial.id!);
                toast.success('Invite resent.');
              } catch (err) {
                toast.error(err instanceof ApiError ? err.message : 'Resend failed.');
              }
            }}
            disabled={resendInviteMut.isPending}
          >
            {resendInviteMut.isPending ? 'Resending…' : 'Resend Invite'}
          </Button>
        ) : null
      }
    >
      {({ form, errorMap }) => (
        <>
          <form.Field name="name">
            {(f) => <Field field={f} label="Full name" formErrorMap={errorMap} />}
          </form.Field>
          <form.Field name="email">
            {(f) => (
              <Field
                field={f}
                label="Email"
                type="email"
                autoComplete="off"
                formErrorMap={errorMap}
              />
            )}
          </form.Field>
          <form.Field name="mobile">
            {(f) => <Field field={f} label="Mobile" formErrorMap={errorMap} />}
          </form.Field>
          <form.Field name="employee_code">
            {(f) => <Field field={f} label="Employee code" formErrorMap={errorMap} />}
          </form.Field>
          <form.Field name="primary_identifier">
            {(f) => (
              <div className="space-y-1.5">
                <label className="text-sm font-medium" htmlFor="field-primary_identifier">
                  Primary identifier
                </label>
                <select
                  id="field-primary_identifier"
                  value={(f.state.value ?? 'EMAIL') as string}
                  onChange={(e) => f.handleChange(e.target.value as never)}
                  className="flex h-9 w-full rounded-md border border-input bg-background px-3 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                >
                  {IDENTIFIER_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </form.Field>
          <form.Field name="password">
            {(f) => (
              <Field
                field={f}
                label={isEditing ? 'New password (leave blank to keep)' : 'Password'}
                type="password"
                autoComplete="new-password"
                formErrorMap={errorMap}
              />
            )}
          </form.Field>
          <form.Field name="role_ids">
            {(f) => (
              <div className="space-y-1.5">
                <span className="text-sm font-medium">Roles</span>
                <div className="max-h-40 space-y-1 overflow-y-auto rounded border p-2">
                  {(roles ?? []).map((role) => {
                    const ids = (f.state.value ?? []) as number[];
                    const checked = ids.includes(role.id);
                    return (
                      <label key={role.id} className="flex items-center gap-2 text-sm">
                        <input
                          type="checkbox"
                          checked={checked}
                          onChange={(e) => {
                            const next = e.target.checked
                              ? [...ids, role.id]
                              : ids.filter((id) => id !== role.id);
                            f.handleChange(next as never);
                          }}
                        />
                        <span>
                          <span className="font-medium">{role.code}</span>
                          <span className="ml-1 text-muted-foreground">{role.name}</span>
                        </span>
                      </label>
                    );
                  })}
                  {(!roles || roles.length === 0) && (
                    <p className="text-xs text-muted-foreground">No roles defined yet.</p>
                  )}
                </div>
              </div>
            )}
          </form.Field>
          <form.Field name="is_staff">
            {(f) => (
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={!!f.state.value}
                  onChange={(e) => f.handleChange(e.target.checked as never)}
                />
                Staff (can access admin)
              </label>
            )}
          </form.Field>
          {isEditing && initial.id != null && <BranchAccessSection userId={initial.id} />}
        </>
      )}
    </MasterFormBody>
  );
}
