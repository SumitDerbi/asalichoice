import { registerModule } from './module-registry';
import { dashboardModule } from '@/modules/dashboard';
import { mastersModule } from '@/modules/masters';
import { catalogModule } from '@/modules/catalog';
import { purchaseModule } from '@/modules/purchase';
import { systemSettingsModule } from '@/modules/system-settings';
import { usersModule } from '@/modules/users';

let registered = false;

/** Idempotent — safe to call from main.tsx and tests. */
export function registerAllModules(): void {
  if (registered) return;
  registered = true;
  registerModule(dashboardModule());
  registerModule(mastersModule());
  registerModule(catalogModule());
  registerModule(purchaseModule());
  registerModule(usersModule());
  registerModule(systemSettingsModule());
}
