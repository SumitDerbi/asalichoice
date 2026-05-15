// Root ESLint flat config: re-exports the admin-ui workspace config so that
// `eslint <files>` can run from the repo root (lint-staged + CI) and still
// pick up the same rules used by `npm run lint --workspace admin-ui`.
// Admin-UI is currently the only JS/TS workspace.
import adminUiConfig from './admin-ui/eslint.config.js';

export default adminUiConfig;
