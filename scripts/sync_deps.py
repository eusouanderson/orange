import os
import subprocess

import tomlkit

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC_DIR = os.path.join(ROOT_DIR, 'src')
REQ_FILE = os.path.join(ROOT_DIR, 'requirements.txt')
PYPROJECT_FILE = os.path.join(ROOT_DIR, 'pyproject.toml')


def run_pipreqs():
    print("🔍 Executando pipreqs na pasta 'src/'...")
    subprocess.run(
        ['pipreqs', SRC_DIR, '--force', '--savepath', REQ_FILE], check=True
    )


def extract_packages():
    with open(REQ_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return sorted({
        line.split('==')[0].strip()
        for line in lines
        if line.strip() and not line.startswith('#')
    })


def update_pyproject(packages):
    with open(PYPROJECT_FILE, 'r', encoding='utf-8') as f:
        toml_data = tomlkit.parse(f.read())

    deps = toml_data['tool']['poetry']['dependencies']
    toml_data['tool']['poetry']['dependencies'] = {
        'python': deps.get('python', '^3.11')
    }

    for pkg in packages:
        toml_data['tool']['poetry']['dependencies'][pkg] = '*'

    with open(PYPROJECT_FILE, 'w', encoding='utf-8') as f:
        f.write(tomlkit.dumps(toml_data))

    print(f'✅ pyproject.toml atualizado com {len(packages)} dependência(s).')


def run_deptry():
    print('📦 Executando deptry para verificar dependências não utilizadas...')
    subprocess.run(['deptry', ROOT_DIR], check=False)


if __name__ == '__main__':
    run_pipreqs()
    pkgs = extract_packages()
    print(f'📦 Pacotes detectados: {pkgs}')
    update_pyproject(pkgs)
    run_deptry()
