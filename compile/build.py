import os
import sys
import subprocess
import shutil
import logging
import zipfile



logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def resource_path(relative_path):
    """Obtém o caminho correto para recursos (imagens, etc.), dependendo se está no ambiente de desenvolvimento ou no executável compilado."""
    try:

        base_path = sys._MEIPASS
    except Exception:

        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def copy_src_files(src_dir, output_dir):
    """Copia todos os arquivos e subdiretórios dentro de src para o diretório de saída."""
    for item in os.listdir(src_dir):
        s = os.path.join(src_dir, item)
        d = os.path.join(output_dir, item)
        if os.path.isdir(s):
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)


def clean_output_dir(output_dir, exe_name):
    """Limpa o diretório de saída, mas mantém o arquivo .exe."""
    if os.path.exists(output_dir):

        for item in os.listdir(output_dir):
            item_path = os.path.join(output_dir, item)

            if item != exe_name:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)


def compile_in_c_executable():
    """Função para compilar o main em cython"""

    project_dir = os.path.dirname(os.path.abspath(__file__))
    logger.info(f"Projeto localizado em: {project_dir}")

    output_dir = os.path.join(project_dir, "..", "dist")
    logger.info(f"Diretório de saída: {output_dir}")

    script_name = os.path.join(project_dir, "..", "src", "core", "main.py")
    logger.info(f"Script principal: {script_name}")

    command = [
        "poetry",
        "run",
        "cython",
        script_name,
    ]

    logger.info(f"Compilando com Cython: {command}")

    try:
        result = subprocess.run(
            command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        logger.info(f"Saída: {result.stdout.decode()}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao compilar: {e.stderr.decode()}")
        raise

def compacter():
    """Função para compactar o projeto em um arquivo zip."""
    project_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(project_dir, "..", "dist")
    zip_file = os.path.join(output_dir, "app.zip")
    
    os.makedirs(output_dir, exist_ok=True)

    
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                file_path = os.path.join(root, file)
                
                arcname = os.path.relpath(file_path, output_dir)
                zipf.write(file_path, arcname)

    logger.info(f"Projeto compactado com sucesso em: {zip_file}")

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

    copy_src_files(src_dir, output_dir)

    command = [
        "pyinstaller",
        "--onefile",
        #"--noconsole",
        "--hidden-import=config",
        f"--add-data={output_dir}{os.pathsep}.",
        "--distpath",
        output_dir,
        "--workpath",
        os.path.join(project_dir, "build"),
        "--specpath",
        os.path.join(project_dir, "specs"),
        "--clean",
        "--name",
        "Orange",
        script_name,
    ]

    if platform in ["windows", "linux"]:
        command.append(f"--icon={icon_path}")

    logger.info(f"Compilando para {platform}...")
    subprocess.run(command)
    clean_output_dir(output_dir, "Orange.exe" if platform == "windows" else "Orange")

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
    tag = sys.argv[2]
    if platform not in ["windows", "linux"]:
        logger.error("Plataforma inválida. Escolha entre 'windows' ou 'linux'.")
        sys.exit(1)

    repo = "eusouanderson/orange"
    release_name = f"Orange {tag}"

    compile_in_c_executable()

    executable_path = build_executable(platform)

    compacter()

    logger.info(f"Compilação concluída: {executable_path}")

    upload_to_github_release(executable_path, tag, release_name, repo, platform)

    '''shutil.rmtree(os.path.join(os.getcwd(), "specs"))
    shutil.rmtree(os.path.join(os.getcwd(), "build"))'''


if __name__ == "__main__":
    main()
