import os
import sys

here = os.path.abspath(os.path.dirname(__file__))
src = os.path.join(here, "src")
sys.path.append(src)

from setuptools import find_packages, setup
from stay import load

meta = {}

with open("META.stay") as f:
    for meta in load(f):
        pass

with open("README.md") as f:
    LONG_DESCRIPTION = f.read()

setup(
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    zip_safe=False,
    **meta
)
