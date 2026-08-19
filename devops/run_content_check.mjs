// Runs check_content.py --strict from npm, whatever the interpreter is called here.
//
// `npm run build` used to hardcode `python`. That works on Windows and breaks on most
// Linux images, where the binary is `python3` and `python` may not exist at all — which
// would have turned every Cloudflare Pages deploy into a failure the moment the gate was
// wired into the build. Node is guaranteed present (npm just started it), so resolve the
// interpreter here instead of betting on one name.
//
// This does NOT soften the gate: if no interpreter is found, the build fails loudly with
// an explanation. A check that skips itself when its runtime is missing is not a check.
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
const script = path.join(here, 'check_content.py');
const candidates = ['python3', 'python', 'py'];

for (const exe of candidates) {
  // `--version` is the cheapest way to tell a real interpreter from the Windows Store
  // stub, which exists on PATH, exits non-zero and prints nothing useful.
  const probe = spawnSync(exe, ['--version'], { encoding: 'utf8' });
  if (probe.error || probe.status !== 0) continue;

  const run = spawnSync(exe, [script, '--strict'], {
    stdio: 'inherit',
    env: { ...process.env, PYTHONIOENCODING: 'utf-8' },
  });
  process.exit(run.status ?? 1);
}

console.error(
  '\ncheck_content.py could not run: no Python 3 found (tried: ' +
    candidates.join(', ') +
    ').\n' +
    'The content gate is required for a build. Install Python 3, or if this is a build\n' +
    'image that genuinely cannot have it, use `npm run build:deploy` — content is already\n' +
    'gated by .github/workflows/content_gate.yml before anything reaches main.\n'
);
process.exit(1);
