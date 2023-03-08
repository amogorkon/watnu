import asyncio
import functools
import time

import use
from PyQt6 import QtCore, QtGui, QtWidgets

qasync = use(
    "qasync",
    version="0.23.0",
    modes=use.auto_install,
    hash_algo=use.Hash.sha256,
    hashes={
        "S㡦櫟唇紤鑗橇㗍䥖䝇于讵誜註裋掟聃肎",  # py3-any
    },
)


async def master():
    progress = QtWidgets.QProgressBar()
    progress.setRange(0, 99)
    progress.show()

    await first_50(progress)
    loop = asyncio.get_running_loop()
    with qasync.QThreadExecutor(1) as exec:
        await loop.run_in_executor(exec, functools.partial(last_50, progress), loop)


async def first_50(progress):
    for i in range(50):
        progress.setValue(i)
        await asyncio.sleep(0.1)


def last_50(progress, loop):
    for i in range(50, 100):
        loop.call_soon_threadsafe(progress.setValue, i)
        time.sleep(0.1)


qasync.run(master())
