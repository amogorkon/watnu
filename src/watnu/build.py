import subprocess
from pathlib import Path
from shutil import copyfile, make_archive, rmtree
from time import time

from main import __version__

before = time()

dst = Path("G:/Watnu/")
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
from platform import platform

make_archive(f"G:/Watnu-dist/Watnu-{'.'.join(str(x) for x in __version__)}-{platform(terse=True)}", "zip", "G:/Watnu-dist/main")

print(f"\nFinished building in {time() - before:.2f} seconds.")
