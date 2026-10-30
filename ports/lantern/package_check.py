"""Windows smoke checks: exercise the shipped embedded Python, not the CI Python."""
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(sys.argv[1]).resolve()
python = root / 'engine/tools/python/python.exe'
scripts = root / 'engine/scripts'
subprocess.run([python, '-c', 'import mods, prepare, online, patches, engine_assets; print("Preparation imports OK")'],
               cwd=root, check=True)
with tempfile.TemporaryDirectory() as data:
    env = dict(os.environ, BB_DATA_DIR=data, BB_CONFIG=str(Path(data) / 'lantern.ini'),
               BB_ONLINE_PAUSED='1', PYTHONUTF8='1')
    result = subprocess.run([python, scripts / 'run_windows.py', '--game-dir', str(Path(data) / 'missing-game')],
                            cwd=root, env=env, capture_output=True, text=True, encoding='utf-8')
    print(result.stdout)
    print(result.stderr)
    if result.returncode != 1 or 'No eboot.bin' not in result.stderr:
        raise RuntimeError('Packaged preparation entry point did not reach game detection')
# The shipped settings (copied to lantern.ini by the launcher in a folder without settings).
ini = (root / 'engine/lantern.default.ini').read_text()
assert 'hdr_mode=nativeplus' in ini and 'hdr_tonemapper=5' in ini
assert not (root / 'bbport.ini').exists() and not (root / 'lantern.ini').exists()
# Left to the display's peak (hdr_peak_auto) and the engine's paper white.
assert not any(line.split('=', 1)[0] in ('hdr_peak', 'hdr_paper_white') for line in ini.splitlines())
# The package's engine id is the launcher's (Updater.EngineId): the updater downloads the whole
# package only when a release's id differs from the installed one, the launcher alone otherwise.
engine = json.loads((root / 'package.json').read_text(encoding='utf-8'))['engine']
updater = (Path(__file__).resolve().parents[2] / 'launcher/windows/BloodborneLauncher/Core/Updater.cs').read_text(encoding='utf-8')
launcher_engine = re.search(r'EngineId = "([^"]+)"', updater).group(1)
assert engine == launcher_engine, f'package.json engine {engine} differs from Updater.EngineId {launcher_engine}'
print('Packaged Python and game-detection smoke check passed; an in-game launch is still required.')
