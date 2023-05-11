from pathlib import Path
from subprocess import run

ui_path = Path("./src/ui")


for path in ui_path.glob("*.ui"):
    args = [r"C:\Users\micro\AppData\Local\Programs\Python\Python311\Scripts\pyuic6.exe", path, "-o", f"src/ui/{path.stem}.py"]
    print(args)
    rc = run(args)
    (Path("./src/ux") / path.name).with_suffix(".py").touch()


Path("./src/ui/__init__.py").write_text(f"""
# generated via qt2py.py
from . import (
{', '.join(p.stem for p in ui_path.glob("*.py"))}
)
""")

Path("./src/ux/__init__.py").write_text(f"""
# generated via qt2py.py
from . import (
{', '.join(p.stem for p in ui_path.glob("*.py"))}
)
""")