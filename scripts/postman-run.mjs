#!/usr/bin/env node
/**
 * Run every Postman collection under qa/postman/<group>/collection.json
 * against the environment file passed via --env (default: local).
 *
 * Usage:
 *   node scripts/postman-run.mjs                # uses qa/postman/local.env.json
 *   node scripts/postman-run.mjs --env staging  # uses qa/postman/staging.env.json
 *   node scripts/postman-run.mjs --group auth   # run only one group
 *
 * Newman is loaded on demand (`npx newman`) so the dev install stays light.
 */

import { readdirSync, statSync, existsSync } from 'node:fs';
import { resolve, join } from 'node:path';
import { spawnSync } from 'node:child_process';

const ROOT = resolve(new URL('..', import.meta.url).pathname);
const POSTMAN_DIR = join(ROOT, 'qa', 'postman');

function arg(flag, fallback) {
  const i = process.argv.indexOf(flag);
  return i >= 0 ? process.argv[i + 1] : fallback;
}

const envName = arg('--env', 'local');
const onlyGroup = arg('--group', null);
const envFile = join(POSTMAN_DIR, `${envName}.env.json`);

if (!existsSync(envFile)) {
  console.error(`[postman] environment file not found: ${envFile}`);
  process.exit(2);
}

const groups = readdirSync(POSTMAN_DIR).filter((name) => {
  const p = join(POSTMAN_DIR, name);
  return statSync(p).isDirectory() && existsSync(join(p, 'collection.json'));
});

const targets = onlyGroup ? groups.filter((g) => g === onlyGroup) : groups;
if (targets.length === 0) {
  console.warn('[postman] no collections found; nothing to do');
  process.exit(0);
}

let failed = 0;
for (const group of targets) {
  const collection = join(POSTMAN_DIR, group, 'collection.json');
  console.log(`\n[postman] running ${group} against ${envName}`);
  const result = spawnSync(
    'npx',
    ['--yes', 'newman', 'run', collection, '-e', envFile, '--reporters', 'cli'],
    { stdio: 'inherit', shell: true },
  );
  if (result.status !== 0) failed += 1;
}

if (failed > 0) {
  console.error(`\n[postman] ${failed} collection(s) failed`);
  process.exit(1);
}
console.log('\n[postman] all collections passed');
