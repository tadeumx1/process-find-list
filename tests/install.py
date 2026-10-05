"""Build and install into an isolated virtual environment without network access."""
import json
from pathlib import Path
import subprocess
import sys
import venv


def exercise_install(root):
    env=Path(root)/'installed'
    # Debian's system Python provides setuptools; build a wheel with it, then install
    # into a clean venv. No system packages are made visible in the target venv.
    venv.EnvBuilder(with_pip=False).create(env)
    wheels=Path(root)/'wheels'
    subprocess.run([sys.executable,'setup.py','bdist_wheel','--dist-dir',str(wheels)],
                   check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    python=env/'bin/python'
    subprocess.run([sys.executable,'-m','pip','--python',str(python),'install','--no-index',str(next(wheels.glob('*.whl')))],
                   check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    version=subprocess.check_output([str(env/'bin/wslazy'),'--version'],cwd=root,text=True).strip()
    module=subprocess.check_output([str(python),'-m','wslazy','--version'],cwd=root,text=True).strip()
    requires=json.loads(subprocess.check_output([str(python),'-c',
        'import json,importlib.metadata; print(json.dumps(importlib.metadata.requires("wslazy") or []))'],cwd=root,text=True))
    return {'version':version,'module':module,'requires':requires}
