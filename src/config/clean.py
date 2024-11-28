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
            # Remover arquivos dos diretórios temporários
            for dir_path in [path_dir3, path_dir1]:
                if os.path.exists(dir_path):
                    for f in os.listdir(dir_path):
                        file_path = os.path.join(dir_path, f)
                        try:
                            print(f"Removendo {f} de {dir_path}")
                            os.remove(file_path)
                        except PermissionError:
                            print(f"Permissão negada para remover {file_path}")

            # Executar comandos para limpeza do sistema
            subprocess.run(["runas", "/user:Administrator", clean_cmd], shell=True)  # Exigir privilégios de admin
            subprocess.run([cleanmgr, "/sagerun:1"], shell=True)

        except Exception as e:
            print(f"Erro ao limpar arquivos no Windows: {e}")

    elif os_type == 'Linux':
        
        path_dir = "/tmp"
        path_dir1 = "/var/tmp"
        clean_cmd = "rm -rf /tmp/*"
        
        try:
            # Remover arquivos dos diretórios temporários
            for dir_path in [path_dir, path_dir1]:
                if os.path.exists(dir_path):
                    for f in os.listdir(dir_path):
                        file_path = os.path.join(dir_path, f)
                        try:
                            print(f"Removendo {f} de {dir_path}")
                            if os.path.isfile(file_path):
                                os.remove(file_path)
                            elif os.path.isdir(file_path):
                                shutil.rmtree(file_path)
                        except PermissionError:
                            print(f"Permissão negada para remover {file_path}")
            
            # Executar comandos para limpeza
            subprocess.run(["sudo", clean_cmd], shell=True)  # Exigir privilégios de sudo
            print("Limpeza concluída no Linux.")

        except Exception as e:
            print(f"Erro ao limpar arquivos no Linux: {e}")

    elif os_type == 'Darwin':  # Para macOS
        
        path_dir = "/tmp"
        path_dir1 = "/var/tmp"
        clean_cmd = "rm -rf /tmp/*"
        
        try:
            # Remover arquivos dos diretórios temporários
            for dir_path in [path_dir, path_dir1]:
                if os.path.exists(dir_path):
                    for f in os.listdir(dir_path):
                        file_path = os.path.join(dir_path, f)
                        try:
                            print(f"Removendo {f} de {dir_path}")
                            if os.path.isfile(file_path):
                                os.remove(file_path)
                            elif os.path.isdir(file_path):
                                shutil.rmtree(file_path)
                        except PermissionError:
                            print(f"Permissão negada para remover {file_path}")
            
            # Executar comandos para limpeza
            subprocess.run(clean_cmd, shell=True)
            print("Limpeza concluída no macOS.")

        except Exception as e:
            print(f"Erro ao limpar arquivos no macOS: {e}")

    else:
        print(f"Sistema operacional {os_type} não suportado para limpeza.")
