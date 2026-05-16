import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { listShortcuts } from './module-registry';

interface ShortcutsOverlayProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const GLOBAL_SHORTCUTS: Array<{ keys: string; label: string }> = [
  { keys: 'Ctrl + K', label: 'Open command palette' },
  { keys: '?', label: 'Show this help' },
  { keys: 'g d', label: 'Go to Dashboard' },
  { keys: 'g m', label: 'Go to Masters' },
  { keys: 't', label: 'Toggle theme' },
  { keys: '[', label: 'Toggle sidebar' },
  { keys: 'Esc', label: 'Close dialogs / drawers' },
];

export function ShortcutsOverlay({ open, onOpenChange }: ShortcutsOverlayProps) {
  const moduleShortcuts = listShortcuts();
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Keyboard shortcuts</DialogTitle>
          <DialogDescription>
            Press the listed key combination to trigger the action.
          </DialogDescription>
        </DialogHeader>
        <ul className="divide-y divide-border">
          {GLOBAL_SHORTCUTS.map((s) => (
            <li key={s.keys} className="flex items-center justify-between py-2 text-sm">
              <span>{s.label}</span>
              <kbd className="rounded border bg-muted px-2 py-0.5 font-mono text-xs">{s.keys}</kbd>
            </li>
          ))}
          {moduleShortcuts.map((s) => (
            <li key={`m-${s.keys}`} className="flex items-center justify-between py-2 text-sm">
              <span>{s.label}</span>
              <kbd className="rounded border bg-muted px-2 py-0.5 font-mono text-xs">{s.keys}</kbd>
            </li>
          ))}
        </ul>
      </DialogContent>
    </Dialog>
  );
}
