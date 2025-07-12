import ast
from pathlib import Path
from tomlkit import parse, dumps

SRC_DIR = Path("src")
PYPROJECT_PATH = Path("./pyproject.toml")


def collect_imports_from_source():
    imports = set()
    for file in SRC_DIR.rglob("*.py"):
        with open(file, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read(), filename=str(file))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for n in node.names:
                            imports.add(n.name.split(".")[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.add(node.module.split(".")[0])
            except Exception as e:
                print(f"[!] Erro ao processar {file}: {e}")
    return imports


def clean_unused_dependencies(imports_used):
    with open(PYPROJECT_PATH, "r", encoding="utf-8") as f:
        toml_data = parse(f.read())

    declared = toml_data["tool"]["poetry"]["dependencies"]
    protected = {"python"}  # nunca remover o python

    to_remove = []

    for dep in declared:
        if dep in protected:
            continue
        if dep.lower() not in map(str.lower, imports_used):
            print(f"[!] Dependência não utilizada detectada: {dep}")
            to_remove.append(dep)

    for dep in to_remove:
        del declared[dep]

    with open(PYPROJECT_PATH, "w", encoding="utf-8") as f:
        f.write(dumps(toml_data))

    print(f"\n✅ Remoção finalizada. {len(to_remove)} dependência(s) removida(s).")


if __name__ == "__main__":
    used = collect_imports_from_source()
    print(f"\n📦 Imports usados no projeto: {sorted(used)}")
    clean_unused_dependencies(used)
