"""Build and install into an isolated virtual environment without network access."""
import json
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import venv


def exercise_install(root):
    env=Path(root)/'installed'
    # Build tooling comes from the development environment. Keep it out of the
    # installed application's environment when exercising the public entry points.
    venv.EnvBuilder(with_pip=False).create(env)
    wheels=Path(root)/'wheels'
    subprocess.run([sys.executable,'setup.py','bdist_wheel','--dist-dir',str(wheels)],
                   check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    python=env/'bin/python'
    subprocess.run([sys.executable,'-m','pip','--python',str(python),'install','--no-index',str(next(wheels.glob('*.whl')))],
                   check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    # Exercise the README's source installation as well as the distributable wheel.
    paths={str(Path(importlib.util.find_spec(name).origin).parent.parent)
           for name in ('setuptools','wheel')}
    build_env={**os.environ,'PYTHONPATH':os.pathsep.join(sorted(paths))}
    subprocess.run([sys.executable,'-m','pip','--python',str(python),'install',
                    '--no-index','--no-build-isolation','--force-reinstall','.'],
                   env=build_env,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    runtime_env={k:v for k,v in os.environ.items() if k not in ('PYTHONPATH','PYTHONHOME')}
    version=subprocess.check_output([str(env/'bin/wslazy'),'--version'],cwd=root,env=runtime_env,text=True).strip()
    module=subprocess.check_output([str(python),'-m','wslazy','--version'],cwd=root,env=runtime_env,text=True).strip()
    requires=json.loads(subprocess.check_output([str(python),'-c',
        'import json,importlib.metadata; print(json.dumps(importlib.metadata.requires("wslazy") or []))'],cwd=root,env=runtime_env,text=True))
    from tests.terminal import exercise_terminal
    interactive=exercise_terminal([str(env/'bin/wslazy')],env=runtime_env,cwd=root)
    return {'version':version,'module':module,'requires':requires,'interactive':interactive}
