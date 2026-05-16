import * as React from 'react';
import { Button } from '@/components/ui/button';
import { Drawer } from '@/components/shared/drawer';

interface DrawerFormProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description?: React.ReactNode;
  /** Submit button label (default ``Save``). Pass null to hide. */
  submitLabel?: string | null;
  /** Cancel button label (default ``Cancel``). Pass null to hide. */
  cancelLabel?: string | null;
  /** Set true while the action is pending. */
  submitting?: boolean;
  /** Click handler for the submit button. */
  onSubmit?: () => void;
  /** Extra footer actions rendered to the left of submit/cancel. */
  extraActions?: React.ReactNode;
  children: React.ReactNode;
}

/**
 * Standardised Create/Edit drawer. Wraps ``<Drawer>`` from
 * ``components/shared/drawer`` with a consistent footer (cancel +
 * submit). The body slot is yours — render the ``<Form>`` and
 * ``form.Field`` blocks inside.
 */
export function DrawerForm({
  open,
  onOpenChange,
  title,
  description,
  submitLabel = 'Save',
  cancelLabel = 'Cancel',
  submitting = false,
  onSubmit,
  extraActions,
  children,
}: DrawerFormProps) {
  const footer = (
    <>
      {extraActions}
      {cancelLabel !== null && (
        <Button
          type="button"
          variant="outline"
          onClick={() => onOpenChange(false)}
          disabled={submitting}
        >
          {cancelLabel ?? 'Cancel'}
        </Button>
      )}
      {submitLabel !== null && (
        <Button type="button" onClick={onSubmit} disabled={submitting}>
          {submitting ? 'Saving...' : (submitLabel ?? 'Save')}
        </Button>
      )}
    </>
  );

  return (
    <Drawer
      open={open}
      onOpenChange={onOpenChange}
      title={title}
      description={description}
      footer={footer}
    >
      {children}
    </Drawer>
  );
}
