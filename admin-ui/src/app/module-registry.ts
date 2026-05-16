import type { ComponentType } from 'react';
import type { RouteObject } from 'react-router-dom';

export type ModuleCategory = 'Operations' | 'Catalog' | 'People' | 'Finance' | 'System';

export interface ShortcutDef {
  keys: string;
  label: string;
}

export interface CommandDef {
  id: string;
  label: string;
  group?: string;
  shortcut?: string;
  perform: () => void;
}

export interface ModuleNavItem {
  to: string;
  label: string;
  end?: boolean;
}

export interface ModuleDef {
  id: string;
  label: string;
  icon: ComponentType<{ className?: string }>;
  category: ModuleCategory;
  order: number;
  routes: RouteObject[];
  nav?: ModuleNavItem[];
  commands?: CommandDef[];
  shortcuts?: ShortcutDef[];
}

const modules: ModuleDef[] = [];

export function registerModule(def: ModuleDef): void {
  if (modules.some((m) => m.id === def.id)) return;
  modules.push(def);
  modules.sort((a, b) => a.order - b.order);
}

export function listModules(): ModuleDef[] {
  return modules.slice();
}

export function listModulesByCategory(): Array<{ category: ModuleCategory; modules: ModuleDef[] }> {
  const order: ModuleCategory[] = ['Operations', 'Catalog', 'People', 'Finance', 'System'];
  return order
    .map((category) => ({
      category,
      modules: modules.filter((m) => m.category === category),
    }))
    .filter((g) => g.modules.length > 0);
}

export function listRoutes(): RouteObject[] {
  return modules.flatMap((m) => m.routes);
}

export function listCommands(): CommandDef[] {
  return modules.flatMap((m) => m.commands ?? []);
}

export function listShortcuts(): ShortcutDef[] {
  return modules.flatMap((m) => m.shortcuts ?? []);
}

/** Test-only: clear the registry (vitest reuses module instances across tests). */
export function __resetRegistryForTests(): void {
  modules.length = 0;
}
