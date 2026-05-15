/**
 * lint-staged configuration.
 *
 * Commands here are passed to lint-staged WITHOUT a shell, so they must be a
 * single binary plus arguments — no `cd`, `&&`, pipes, or globs.
 *
 * Layout decisions:
 *   - Root `eslint.config.mjs` re-exports `admin-ui/eslint.config.js`, so
 *     `eslint` invoked from the repo root finds the same rules used by
 *     `npm run lint --workspace admin-ui`.
 *   - Prettier walks up from each file path, so `admin-ui/.prettierrc.json`
 *     and the root config are both honoured automatically.
 *   - Stylelint is given an explicit `--config` pointing at the root config.
 *   - Python files are deliberately NOT handled here; `.husky/pre-commit`
 *     chains `python -m pre_commit run --hook-stage pre-commit` after
 *     lint-staged, which runs ruff (--fix + format), black, and isort with
 *     versions pinned in `.pre-commit-config.yaml`.
 *
 * Binaries (eslint, prettier, stylelint) are hoisted to the root
 * `node_modules/.bin` by npm workspaces, so `npx --no -- <bin>` resolves
 * them from the repo root.
 */
const path = require('node:path');

const ROOT = __dirname;

const toRel = (files) =>
  files.map((f) => `"${path.relative(ROOT, f).split(path.sep).join('/')}"`);

module.exports = {
  'admin-ui/**/*.{ts,tsx,js,jsx,mjs,cjs}': (files) => {
    const list = toRel(files);
    if (list.length === 0) return [];
    return [
      `npx --no -- eslint --fix --max-warnings=0 --no-error-on-unmatched-pattern ${list.join(' ')}`,
      `npx --no -- prettier --write --ignore-unknown ${list.join(' ')}`,
    ];
  },
  'admin-ui/**/*.{css,scss}': (files) => {
    const list = toRel(files);
    if (list.length === 0) return [];
    return [
      `npx --no -- stylelint --fix --allow-empty-input --config .stylelintrc.json ${list.join(' ')}`,
      `npx --no -- prettier --write --ignore-unknown ${list.join(' ')}`,
    ];
  },
  '*.{json,md,yml,yaml,toml}': (files) => {
    const list = toRel(files);
    if (list.length === 0) return [];
    return [`npx --no -- prettier --write --ignore-unknown ${list.join(' ')}`];
  },
};
