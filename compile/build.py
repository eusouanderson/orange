import os
import sys
import subprocess
import shutil
import logging

# Configuração do logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def resource_path(relative_path):
    """Obtém o caminho correto para recursos (imagens, etc.), dependendo se está no ambiente de desenvolvimento ou no executável compilado."""
    try:
        # PyInstaller cria uma pasta temporária com recursos extraídos. Usamos sys._MEIPASS para isso.
        base_path = sys._MEIPASS
    except Exception:
        # Caso o código esteja sendo executado no ambiente de desenvolvimento
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def copy_src_files(src_dir, output_dir):
    """Copia todos os arquivos e subdiretórios dentro de src para o diretório de saída."""
    for item in os.listdir(src_dir):
        s = os.path.join(src_dir, item)
        d = os.path.join(output_dir, item)
        if os.path.isdir(s):
            shutil.copytree(s, d)  # Copia o diretório e seu conteúdo
        else:
            shutil.copy2(s, d)  # Copia o arquivo individual

def clean_output_dir(output_dir, exe_name):
    """Limpa o diretório de saída, mas mantém o arquivo .exe."""
    if os.path.exists(output_dir):
        # Percorre todos os itens dentro do diretório de saída
        for item in os.listdir(output_dir):
            item_path = os.path.join(output_dir, item)

            # Se for o arquivo .exe, não apaga
            if item != exe_name:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)  # Remove diretórios
                else:
                    os.remove(item_path)  # Remove arquivos

def build_executable(platform):
    """Função para compilar o projeto em um executável para o sistema especificado."""
    project_dir = os.path.dirname(os.path.abspath(__file__))
    logger.info(f"Projeto localizado em: {project_dir}")

    output_dir = os.path.join(project_dir, "..", "dist")
    logger.info(f"Diretório de saída: {output_dir}")

    script_name = os.path.join(project_dir, "..", "src", "core", "main.py")
    logger.info(f"Script principal: {script_name}")

    icon_path = os.path.join(
        project_dir, "..", "src", "assets", "images", "icons", "orange.ico"
    )
    
    logger.info(f"Ícone do aplicativo: {icon_path}")

    src_dir = os.path.join(project_dir, "..", "src")
    logger.info(f"Diretório src: {src_dir}")

    logger.info(f"Caminho do separador: {os.pathsep}")

    # Copiar arquivos de src para o diretório de saída
    copy_src_files(src_dir, output_dir)

    # Comando do PyInstaller para incluir todos os arquivos de src
    command = [
        "pyinstaller",
        "--onefile",
        "--noconsole",  # Desabilita a janela de consola
        "--hidden-import=config",
        f"--add-data={output_dir}{os.pathsep}.",  # Inclui os arquivos copiados de src
        "--distpath",
        output_dir,
        "--workpath",
        os.path.join(project_dir, "build"),
        "--specpath",
        os.path.join(project_dir, "specs"),
        "--clean",
        "--name",
        "Orange",  # Nome do executável
        script_name,
    ]

    # Adicionando o ícone do aplicativo, caso o platform seja Windows ou Linux
    if platform in ["windows", "linux"]:
        command.append(f"--icon={icon_path}")

    logger.info(f"Compilando para {platform}...")
    subprocess.run(command)
    clean_output_dir(output_dir, "Orange.exe" if platform == "windows" else "Orange")
    # Retorna o caminho do executável gerado
    return os.path.join(output_dir, "Orange.exe" if platform == "windows" else "Orange")

def upload_to_github_release(file_path, tag, release_name, repo, platform):
    """Faz upload de um arquivo para o release do GitHub usando o CLI do GitHub."""
    logger.info(f"Enviando {file_path} para o release do GitHub...")
    try:
        subprocess.run(
            [
                "gh",
                "release",
                "create",
                tag,
                file_path,
                "--repo",
                repo,
                "--title",
                release_name,
                "--notes",
                f"Release {release_name} Platform: {platform}",
            ],
            check=True,
        )
        logger.info("Upload concluído com sucesso.")
    except subprocess.CalledProcessError as e:
        logger.error("Erro ao enviar para o GitHub Release:", e)
        sys.exit(1)

def main():
    if len(sys.argv) < 3:
        logger.error("Uso: python build.py <platform> <tag>")
        logger.error("Plataformas: windows, linux")
        sys.exit(1)
    
    
    platform = sys.argv[1].lower()
    tag = sys.argv[2]  # O tag do release, por exemplo: v1.0.0

    if platform not in ["windows", "linux"]:
        logger.error("Plataforma inválida. Escolha entre 'windows' ou 'linux'.")
        sys.exit(1)

    # Configurações do release
    repo = "eusouanderson/orange"
    release_name = f"Orange {tag}"

    # Build do executável
    executable_path = build_executable(platform)
    logger.info(f"Compilação concluída: {executable_path}")

    # Upload do executável para o release
    upload_to_github_release(executable_path, tag, release_name, repo, platform)

if __name__ == "__main__":
    main()
