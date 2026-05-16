/**
 * Vitest MSW server. Started/stopped in `tests/setup.ts`.
 *
 * Use `server.use(...overrides)` inside individual tests to swap handlers
 * for a single case. `server.resetHandlers()` runs after each test.
 */

import { setupServer } from 'msw/node';
import { handlers } from './handlers';
import { masterHandlers } from './master-handlers';

export const server = setupServer(...handlers, ...masterHandlers);
