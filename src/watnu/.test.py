from pathlib import Path
import subprocess

#link = r'C:\Users\micro\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\Watnu.lnk'
#target = r"G:\Watnu-dist\Watnu-0.1.2-Windows-10 (nightly 2021-03-02.5093)\Watnu.exe"
#subprocess.run(['MKLINK', link, target])
import sys

Path(__file__).resolve()

stats = {1:2, 3:4, 4:1}

print(max(stats.items(), key=lambda i: i[1]))