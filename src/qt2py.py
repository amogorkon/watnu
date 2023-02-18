from pathlib import Path
from subprocess import run

path = Path("./ui")

for name in path.glob("*.ui"):
    args = [r"C:\Users\micro\AppData\Local\Programs\Python\Python311\Scripts\pyuic6.exe", name, "-o", f"ui/{name.stem}.py"]
    print(args)
    rc = run(args)