import * as React from 'react';
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandList,
} from '@/components/ui/command';

/**
 * Module-registerable command palette item. Modules call
 * `registerCommands([...])` at module-load time to add entries.
 */
export interface CommandEntry {
  id: string;
  label: string;
  group?: string;
  shortcut?: string;
  perform: () => void;
}

const registry: Map<string, CommandEntry> = new Map();
const subscribers = new Set<() => void>();

export function registerCommands(entries: CommandEntry[]) {
  entries.forEach((e) => registry.set(e.id, e));
  subscribers.forEach((fn) => fn());
}

export function useCommandRegistry(): CommandEntry[] {
  const [, force] = React.useReducer((n: number) => n + 1, 0);
  React.useEffect(() => {
    const fn = () => force();
    subscribers.add(fn);
    return () => {
      subscribers.delete(fn);
    };
  }, []);
  return Array.from(registry.values());
}

interface CommandPaletteProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function CommandPalette({ open, onOpenChange }: CommandPaletteProps) {
  const entries = useCommandRegistry();
  const grouped = React.useMemo(() => {
    const map = new Map<string, CommandEntry[]>();
    entries.forEach((e) => {
      const key = e.group ?? 'General';
      const list = map.get(key) ?? [];
      list.push(e);
      map.set(key, list);
    });
    return Array.from(map.entries());
  }, [entries]);

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
