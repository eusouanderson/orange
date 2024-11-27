import os
import platform
import subprocess
import shutil

def clean():
    
    os_type = platform.system()

    if os_type == 'Windows':
        
        path_dir = r"C:\Users\ADMINI~1\AppData\Local\Temp"
        path_dir1 = r"C:\Windows\Temp"
        path_dir2 = r"C:\Windows\system32\WSReset.exe"
        path_dir3 = r"C:\Windows\Downloaded Program Files"
        clean_cmd = "del /q/f/s %temp%\\*"
        cmd = r"C:\Windows\system32\cmd.exe"
        cleanmgr = r"C:\Windows\system32\cleanmgr.exe"

        
        try:
            for f in os.listdir(path_dir3):
                print(f"Removendo {f} de {path_dir3}")
                os.remove(os.path.join(path_dir3, f))

            for f in os.listdir(path_dir1):
                print(f"Removendo {f} de {path_dir1}")
                os.remove(os.path.join(path_dir1, f))

            
            subprocess.run(clean_cmd, shell=True)
            subprocess.run([cleanmgr, "/sagerun:1"], shell=True)  

        except Exception as e:
            print(f"Erro ao limpar arquivos no Windows: {e}")

    elif os_type == 'Linux':
        
        path_dir = "/tmp"
        path_dir1 = "/var/tmp"
        clean_cmd = "rm -rf /tmp/*"
        
        try:
            for dir_path in [path_dir, path_dir1]:
                if os.path.exists(dir_path):
                    for f in os.listdir(dir_path):
                        print(f"Removendo {f} de {dir_path}")
                        file_path = os.path.join(dir_path, f)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)

            
            subprocess.run(clean_cmd, shell=True)
            print("Limpeza concluída no Linux.")

        except Exception as e:
            print(f"Erro ao limpar arquivos no Linux: {e}")

    elif os_type == 'Darwin':  
        
        path_dir = "/tmp"
        path_dir1 = "/var/tmp"
        clean_cmd = "rm -rf /tmp/*"
        
        try:
            for dir_path in [path_dir, path_dir1]:
                if os.path.exists(dir_path):
                    for f in os.listdir(dir_path):
                        print(f"Removendo {f} de {dir_path}")
                        file_path = os.path.join(dir_path, f)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)

            
            subprocess.run(clean_cmd, shell=True)
            print("Limpeza concluída no macOS.")

        except Exception as e:
            print(f"Erro ao limpar arquivos no macOS: {e}")

    else:
        print(f"Sistema operacional {os_type} não suportado para limpeza.")



