from pathlib import Path
from subprocess import run

path = Path("./ui")

for name in path.glob("*.ui"):
    args = ["pyuic5", name, "-o", "ui/" + name.stem + ".py"]
    print(args)
    rc = run(args)

path = Path(".")
print("icons:")
for name in path.glob("*.qrc"):
    print(name)
    args = ["pyrcc5", name, "-o", name.stem + "_rc.py"]
    print(args)
    rc = run(args)
