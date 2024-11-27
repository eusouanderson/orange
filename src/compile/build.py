import os
import sys
import subprocess

def build_executable(platform):
    """Função para compilar o projeto em um executável para o sistema especificado."""
    # Diretório do seu projeto
    project_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(project_dir, 'dist')

    # Caminho para o script principal
    script_name = os.path.join(project_dir, '..', 'core', 'main.py')
    icon_path = os.path.join(project_dir, 'assets', 'images', 'background', 'orange.png')

    # Comando base para o PyInstaller
    command = [
        'pyinstaller',
        '--onefile',
        '--distpath', output_dir,
        '--workpath', os.path.join(project_dir, 'build'),
        '--specpath', os.path.join(project_dir, 'specs'),
        '--clean',
        '--name', 'Orange',  # Nome do executável
        script_name
    ]

    if platform in ['windows', 'linux']:
        command.append(f'--icon={icon_path}')

    print(f"Building for {platform}...")
    subprocess.run(command)

    return os.path.join(output_dir, 'Orange.exe' if platform == 'windows' else 'Orange')


def upload_to_github_release(file_path, tag, release_name, repo, platform):
    """Faz upload de um arquivo para o release do GitHub usando o CLI do GitHub."""
    print(f"Uploading {file_path} to GitHub release...")
    try:
        subprocess.run([
            'gh', 'release', 'create', tag, file_path,
            '--repo', repo,
            '--title', release_name,
            '--notes', f'Release {release_name} Platform: {platform}' 
        ], check=True)
        print("Upload completed successfully.")
    except subprocess.CalledProcessError as e:
        print("Error uploading to GitHub Release:", e)
        sys.exit(1)


def main():
    if len(sys.argv) < 3:
        print("Usage: python build.py <platform> <tag>")
        print("Platforms: windows, linux")
        sys.exit(1)

    platform = sys.argv[1].lower()
    tag = sys.argv[2]  # O tag do release, por exemplo: v1.0.0

    if platform not in ['windows', 'linux']:
        print("Invalid platform. Choose either 'windows' or 'linux'.")
        sys.exit(1)

    # Configurações do release
    repo = "eusouanderson/orange"  
    release_name = f"Orange {tag}"

    # Build do executável
    executable_path = build_executable(platform)
    print(f"Build complete: {executable_path}")

    # Upload do executável para o release
    upload_to_github_release(executable_path, tag, release_name, repo, platform)


if __name__ == '__main__':
    main()
