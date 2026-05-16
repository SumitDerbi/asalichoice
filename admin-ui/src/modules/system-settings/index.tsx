import { Settings } from 'lucide-react';
import type { ModuleDef } from '@/app/module-registry';
import { SystemSettingsPage } from './system-settings-page';

export function systemSettingsModule(): ModuleDef {
  return {
    id: 'system-settings',
    label: 'System Settings',
    icon: Settings,
    category: 'System',
    order: 100,
    routes: [{ path: 'system-settings/*', element: <SystemSettingsPage /> }],
    nav: [{ to: '/system-settings', label: 'System Settings' }],
    commands: [
      {
        id: 'system-settings.open',
        label: 'Open system settings',
        group: 'Navigation',
        perform: () => {
          window.location.assign('/system-settings');
        },
      },
    ],
    shortcuts: [
      {
        keys: 'g s',
        label: 'Go to system settings',
      },
    ],
  };
}
