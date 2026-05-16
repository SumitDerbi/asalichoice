import { LayoutDashboard } from 'lucide-react';
import { DashboardPage } from './dashboard-page';
import type { ModuleDef } from '@/app/module-registry';

export function dashboardModule(): ModuleDef {
  return {
    id: 'dashboard',
    label: 'Dashboard',
    icon: LayoutDashboard,
    category: 'Operations',
    order: 0,
    routes: [{ index: true, element: <DashboardPage /> }],
    nav: [{ to: '/', label: 'Dashboard', end: true }],
    commands: [
      {
        id: 'dashboard.open',
        label: 'Open dashboard',
        group: 'Navigation',
        perform: () => {
          window.location.assign('/');
        },
      },
    ],
  };
}
