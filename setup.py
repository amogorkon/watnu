import os
import pathlib
import sys

here = os.path.abspath(os.path.dirname(__file__))
src = os.path.join(here, "src")
sys.path.append(src)

import use
from setuptools import find_packages, setup

meta = {}
load = use(
    use.URL("https://raw.githubusercontent.com/amogorkon/stay/master/src/stay/stay.py"),
    modes=use.recklessness,
).Decoder()

with open("META.stay") as f:
    for meta in load(f):
        pass

LONG_DESCRIPTION = pathlib.Path("README.md").read_text()
setup(
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    zip_safe=False,
    **meta
)
