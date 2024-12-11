import os
import sys
import subprocess
import shutil
import logging
import zipfile

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def ensure_dir_exists(directory):
    """Cria um diretório, se não existir."""
    os.makedirs(directory, exist_ok=True)


def resource_path(relative_path):
    """Obtém o caminho correto para recursos dependendo do ambiente."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def clean_output_dir(output_dir, exe_name=None):
    """Limpa o diretório de saída, mantendo o executável, se especificado."""
    if os.path.exists(output_dir):
        for item in os.listdir(output_dir):
            item_path = os.path.join(output_dir, item)
            if exe_name and item == exe_name:
                continue
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
    logger.info("Diretório de saída limpo.")


def prepare_pyx(source_file, pyx_file):
    """Cria um arquivo .pyx a partir de um script Python."""
    try:
        shutil.copy(source_file, pyx_file)
        logger.info(f"Arquivo .pyx gerado: {pyx_file}")
    except Exception as e:
        logger.error(f"Erro ao criar o arquivo .pyx: {e}")
        raise


def copy_src_files(src_dir, output_dir):
    """Função para copiar arquivos do diretório src para o diretório de saída, excluindo a pasta 'core'."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for item in os.listdir(src_dir):
        if item == "core":
            continue

        s = os.path.join(src_dir, item)
        d = os.path.join(output_dir, item)

        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)

    logger.info(
        f"Arquivos copiados de {src_dir} para {output_dir}, exceto a pasta 'core'"
    )


def compile_pyx_to_c(pyx_file, output_dir):
    """Compila o arquivo .pyx para C."""
    output_c_file = os.path.join(
        output_dir, os.path.basename(pyx_file).replace(".pyx", ".c")
    )
    command = ["cython", "-3", "-o", output_c_file, pyx_file]
    logger.info(f"Compilando .pyx para .c: {command}")
    try:
        subprocess.run(
            command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        logger.info(f"Arquivo .c gerado: {output_c_file}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao compilar .pyx: {e.stderr.decode()}")
        raise


def compile_all_src_files(src_dir, output_dir):
    """Compila todos os arquivos Python em src_dir para arquivos .pyx e depois para .c."""
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".py"):
                py_file = os.path.join(root, file)
                pyx_file = os.path.join(output_dir, f"{os.path.splitext(file)[0]}.pyx")
                prepare_pyx(py_file, pyx_file)
                compile_pyx_to_c(pyx_file, output_dir)


def build_executable(platform, script_path, output_dir, icon_path, compile_all=False):
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

    if compile_all:
        compile_all_src_files(src_dir, output_dir)
    else:
        pyx_file = os.path.join(src_dir, "core", "main.py")
        prepare_pyx(pyx_file, os.path.join(output_dir, "main.pyx"))
        compile_pyx_to_c(os.path.join(output_dir, "main.pyx"), output_dir)

    copy_src_files(src_dir, output_dir)

    upx_dir = os.path.join(project_dir, "upx")

    command = [
        "pyinstaller",
        "--onefile",
        "--noconsole",
        "--hidden-import=config",
        "--hidden-import=PySide6",
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
        f"--upx-dir={upx_dir}",
    ]

    if platform in ["windows", "linux"]:
        command.append(f"--icon={icon_path}")

    logger.info(f"Compilando para {platform}...")

    try:
        result = subprocess.run(
            command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        logger.info(f"Compilação bem-sucedida: {result.stdout.decode()}")
    except subprocess.CalledProcessError as e:
        error_message = (
            e.stderr.decode() if e.stderr else "Nenhuma saída de erro disponível"
        )
        logger.error(f"Erro durante a compilação: {error_message}")
        logger.error(f"Código de retorno: {e.returncode}")
        logger.error(
            f"Saída completa: {e.output.decode() if e.output else 'Sem saída'}"
        )
        sys.exit(1)

    clean_output_dir(output_dir, "Orange.exe" if platform == "windows" else "Orange")

    return os.path.join(output_dir, "Orange.exe" if platform == "windows" else "Orange")


def compact_output(output_dir, zip_path):
    """Compacta o conteúdo do diretório de saída em um arquivo ZIP."""
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                file_path = os.path.join(root, file)

                if file_path == zip_path:
                    continue
                arcname = os.path.relpath(file_path, output_dir)
                zipf.write(file_path, arcname)

    logger.info(f"Projeto compactado em: {zip_path}")


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


def commit_and_push_changes(repo, tag, commit_message="Atualização do build com src"):
    """Faz commit e push das alterações no repositório Git."""
    try:
        #subprocess.run(["git", "remote", "set-url", "origin", repo], check=True)
        logger.info(f"Repositório remoto configurado para: {repo}")

        subprocess.run(["git", "add", "."], check=True)

        subprocess.run(["git", "commit", "-m", commit_message], check=True)

        subprocess.run(["git", "push", "origin", "main"], check=True)

        logger.info(
            "Alterações comprometidas e enviadas para o repositório com sucesso."
        )
    except subprocess.CalledProcessError as e:
        logger.error("Erro ao fazer commit ou push no repositório Git:", e)
        sys.exit(1)


def main():
    if len(sys.argv) < 3:
        logger.error("Uso: python build.py <platform> <tag> [repo] [--compile-all]")
        logger.error("Plataformas: windows, linux")
        logger.error("[repo]: Repositório GitHub para upload.")
        logger.error("[--compile-all]: Compilar todos os arquivos Python.")
        sys.exit(1)

    platform = sys.argv[1].lower()
    tag = sys.argv[2]
    compile_all = "--compile-all" in sys.argv

    repo = (
        sys.argv[3]
        if len(sys.argv) > 3 and not sys.argv[3].startswith("--")
        else "eusouanderson/orange_calculator"
    )

    if platform not in ["windows", "linux"]:
        logger.error("Plataforma inválida. Escolha entre 'windows' ou 'linux'.")
        sys.exit(1)

    project_dir = os.path.abspath(os.path.dirname(__file__))
    output_dir = "dist"
    script_path = os.path.join(project_dir, "src", "core", "main.py")
    icon_path = os.path.join(
        project_dir, "src", "assets", "images", "icons", "orange.ico"
    )
    zip_path = os.path.join(output_dir, f"Orange-{tag}.zip")

    try:
        #console_commit_input = input("Digite o commit para o repositório: ").strip()
        #console_repo_input = input("Digite o repositório para o upload: ").strip()

        '''if not console_commit_input or not console_repo_input:
            raise ValueError("Commit ou repositório inválidos.")'''

        clean_output_dir(output_dir)
        build_executable(platform, script_path, output_dir, icon_path, compile_all)
        compact_output(output_dir, zip_path)

        #commit_and_push_changes(repo, tag)
        upload_to_github_release(zip_path, tag, f"Orange {tag}", repo, platform)
    except subprocess.CalledProcessError as e:
        logger.error("Erro ao executar subprocesso: %s", e.stderr.decode())
    except Exception as e:
        logger.error("Erro durante a execução: %s", str(e))


if __name__ == "__main__":
    main()
