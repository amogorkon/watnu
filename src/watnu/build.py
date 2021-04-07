import subprocess
import sys
from pathlib import Path
from shutil import copyfile, make_archive, rmtree
from time import time

from main import __version__

before = time()

dst = Path("G:/Watnu/")

print(Path(__file__).absolute().parents[0])
sys.path.append(Path(__file__).absolute().parents[0])

completed = subprocess.run(["pytest", "../../test", "-x", "-v"])
if completed.returncode:
    print("Tests failed, aborting.")
    sys.exit()

try:
    dst.mkdir(parents=True)
except FileExistsError:
    rmtree(dst)
    dst.mkdir(parents=True)

exclude = ["watnu.sqlite", 
            "config.stay", 
            "qt2py.py", 
            "build.py", 
            "*.ipynb*", 
            "*checkpoint*",
            ]

exclude_folders = [".ropeproject", 
                    "__pycache__",
                    "exo 2", 
                    "build", 
                    "logs", 
                    "Include",
                    ]

src = Path(".")

for p in src.glob("**/*"):
    if any(part in p.parts for part in exclude_folders) or any(p.match(part) for part in exclude):
        continue
    if p.is_dir():
        (dst / p).mkdir(parents=True)
    else:
        copyfile(p, dst / p)


subprocess.run(["pyinstaller", "--distpath", "G:/Watnu-dist", "--workpath", "G:/Watnu-build", "G:/Watnu/main.spec", "-y"])

print("building zip..")
from datetime import date
from math import modf
from platform import platform
from time import localtime


def timestamp2fragday(x):
    now = localtime(x)
    seconds = now.tm_hour*60*60 + now.tm_min*60 + now.tm_sec
    total_seconds = 24*60*60
    return f"{modf(seconds/total_seconds)[0]:.4f}"[1:]
now = time()
make_archive(f"G:/Watnu-dist/Watnu-{'.'.join(str(x) for x in __version__)}-{platform(terse=True)} (nightly {date.fromtimestamp(now)}{timestamp2fragday(now)})", "zip", "G:/Watnu-dist/main")

print(f"\nFinished building in {time() - before:.2f} seconds.")
