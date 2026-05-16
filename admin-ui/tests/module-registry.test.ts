import { describe, expect, it, beforeEach } from 'vitest';
import {
  registerModule,
  listModules,
  listRoutes,
  listCommands,
  listShortcuts,
  listModulesByCategory,
  __resetRegistryForTests,
  type ModuleDef,
} from '@/app/module-registry';
import { Boxes } from 'lucide-react';

function fakeModule(overrides: Partial<ModuleDef> = {}): ModuleDef {
  return {
    id: 'fake',
    label: 'Fake',
    icon: Boxes,
    category: 'Operations',
    order: 100,
    routes: [{ path: 'fake', element: null }],
    nav: [{ to: '/fake', label: 'Fake' }],
    commands: [{ id: 'fake.cmd', label: 'Fake command', perform: () => undefined }],
    shortcuts: [{ keys: 'g f', label: 'Go to Fake' }],
    ...overrides,
  };
}

describe('module registry', () => {
  beforeEach(() => {
    __resetRegistryForTests();
  });

  it('registers and lists modules', () => {
    registerModule(fakeModule({ id: 'a', order: 2 }));
    registerModule(fakeModule({ id: 'b', order: 1 }));
    const all = listModules();
    expect(all).toHaveLength(2);
    // sorted by order ascending
    expect(all[0].id).toBe('b');
    expect(all[1].id).toBe('a');
  });

  it('ignores duplicate ids', () => {
    registerModule(fakeModule({ id: 'dup' }));
    registerModule(fakeModule({ id: 'dup', label: 'Different' }));
    const all = listModules();
    expect(all).toHaveLength(1);
    expect(all[0].label).toBe('Fake');
  });

  it('groups by category in canonical order', () => {
    registerModule(fakeModule({ id: 'a', category: 'Finance', order: 1 }));
    registerModule(fakeModule({ id: 'b', category: 'Operations', order: 2 }));
    const groups = listModulesByCategory();
    expect(groups.map((g) => g.category)).toEqual(['Operations', 'Finance']);
  });

  it('flattens routes, commands, shortcuts', () => {
    registerModule(fakeModule({ id: 'a' }));
    registerModule(fakeModule({ id: 'b' }));
    expect(listRoutes()).toHaveLength(2);
    expect(listCommands()).toHaveLength(2);
    expect(listShortcuts()).toHaveLength(2);
  });
});
