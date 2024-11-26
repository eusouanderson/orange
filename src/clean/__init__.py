import os


def clean():

    path_dir = r"C:\Users\ADMINI~1\AppData\Local\Temp"
    path_dir1 = r"C:\Windows\Temp"
    path_dir2 = r"C:\Windows\system32\WSReset.exe"
    path_dir3 = r"C:\Windows\Downloaded Program Files"
    clean_cmd = "del /q/f/s %temp%\*"
    cmd = r"C:Windows\system32\cmd.exe"
    cleanmgr = r"C:Windows\system32\cleanmgr.exe"

    for f in os.listdir(path_dir3):
        print(f)
        os.remove(os.path.join(path_dir3, f))
        """os.startfile(cleanmgr)"""

    for f in os.listdir(path_dir1):
        print(len(f))
        os.remove(os.path.join(path_dir1, f))
