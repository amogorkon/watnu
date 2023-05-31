# ruff: noqa

import use

np = use(
    "numpy",
    version="1.24.1",
    modes=use.auto_install,  # type: ignore
    hash_algo=use.Hash.sha256,
    hashes={
        "i㹄臲嬁㯁㜇䕀蓴卄闳䘟菽掸䢋䦼亱弿椊",  # cp311-win_amd64
    },
    import_as="numpy",
)  # type: ignore

import numpy as np

print(np.__version__)
