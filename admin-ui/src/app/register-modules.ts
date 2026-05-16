import { registerModule } from './module-registry';
import { dashboardModule } from '@/modules/dashboard';
import { mastersModule } from '@/modules/masters';

let registered = false;

/** Idempotent — safe to call from main.tsx and tests. */
export function registerAllModules(): void {
  if (registered) return;
  registered = true;
  registerModule(dashboardModule());
  registerModule(mastersModule());
}
