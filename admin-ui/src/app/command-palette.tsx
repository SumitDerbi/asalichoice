import * as React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandList,
} from '@/components/ui/command';
import { listCommands, type CommandDef } from './module-registry';

interface CommandPaletteProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function CommandPalette({ open, onOpenChange }: CommandPaletteProps) {
  const navigate = useNavigate();
  const entries = React.useMemo<CommandDef[]>(() => {
    if (!open) return [];
    return listCommands();
  }, [open]);

  const grouped = React.useMemo(() => {
    const builtins: CommandDef[] = [
      {
        id: 'nav.dashboard',
        label: 'Go to Dashboard',
        group: 'Navigation',
        perform: () => navigate('/'),
      },
      {
        id: 'nav.masters',
        label: 'Go to Masters',
        group: 'Navigation',
        perform: () => navigate('/masters'),
      },
    ];
    const all = [...builtins, ...entries];
    const map = new Map<string, CommandDef[]>();
    all.forEach((e) => {
      const key = e.group ?? 'General';
      const list = map.get(key) ?? [];
      list.push(e);
      map.set(key, list);
    });
    return Array.from(map.entries());
  }, [entries, navigate]);

  return (
    <CommandDialog open={open} onOpenChange={onOpenChange}>
      <CommandInput placeholder="Type a command or search…" />
      <CommandList>
        <CommandEmpty>No results.</CommandEmpty>
        {grouped.map(([group, items]) => (
          <CommandGroup key={group} heading={group}>
            {items.map((item) => (
              <button
                key={item.id}
                type="button"
                className="flex w-full items-center justify-between rounded-sm px-2 py-1.5 text-sm hover:bg-accent"
                onClick={() => {
                  onOpenChange(false);
                  item.perform();
                }}
              >
                <span>{item.label}</span>
                {item.shortcut && (
                  <span className="text-xs text-muted-foreground">{item.shortcut}</span>
                )}
              </button>
            ))}
          </CommandGroup>
        ))}
      </CommandList>
    </CommandDialog>
  );
}
