from pathlib import Path
from subprocess import run

ui_path = Path("./ui")


for path in ui_path.glob("*.ui"):
    args = [r"C:\Users\micro\AppData\Local\Programs\Python\Python311\Scripts\pyuic6.exe", path, "-o", f"ui/{path.stem}.py"]
    print(args)
    rc = run(args)
    (Path("./ux") / path.name).with_suffix(".py").touch()


Path("./ui/__init__.py").write_text(f"""
# generated via qt2py.py
from . import (
{', '.join(p.stem for p in ui_path.glob("*.py"))}
)
""")

Path("./ux/__init__.py").write_text(f"""
# generated via qt2py.py
from . import (
{', '.join(p.stem for p in ui_path.glob("*.py"))}
)
""")