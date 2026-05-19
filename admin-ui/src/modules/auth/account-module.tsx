import { User } from 'lucide-react';
import type { ModuleDef } from '@/app/module-registry';
import { AccountPage } from './account-page';

export function accountModule(): ModuleDef {
  return {
    id: 'account',
    label: 'Account',
    icon: User,
    category: 'People',
    order: 99,
    routes: [
      {
        path: 'account',
        element: <AccountPage />,
      },
    ],
    nav: [{ to: '/account', label: 'My Account', end: true }],
  };
}
