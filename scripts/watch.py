#!/usr/bin/env python3
"""
Watch mode para desenvolvimento: reinicia a aplicação quando arquivos Python mudam.
Uso: python scripts/watch.py
"""

import os
import subprocess
import sys
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# Configurações
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
EXTENSIONS = {".py"}
IGNORE_DIRS = {"__pycache__", ".pytest_cache", ".git"}

process = None


class SourceChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return

        path = Path(event.src_path)
        
        # Ignora diretórios ignorados
        if any(ignored in path.parts for ignored in IGNORE_DIRS):
            return
        
        # Só monitora arquivos Python
        if path.suffix not in EXTENSIONS:
            return

        print(f"\n📝 Mudança detectada: {path.relative_to(SRC_DIR.parent)}")
        self._restart_app()

    def _restart_app(self):
        global process
        
        if process:
            print("🛑 Parando aplicação...")
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
            process = None
        
        time.sleep(0.5)
        print("🚀 Reiniciando aplicação...")
        
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SRC_DIR)
        env["QT_QPA_PLATFORM"] = "xcb"
        
        process = subprocess.Popen(
            [sys.executable, "src/core/main.py"],
            env=env,
            cwd=SRC_DIR.parent,
        )


def main():
    print("👀 Watch mode ativado")
    print(f"📂 Monitorando: {SRC_DIR}")
    print("💡 Dica: salve um arquivo Python para reiniciar a aplicação")
    print("🛑 Pressione Ctrl+C para sair\n")
    
    handler = SourceChangeHandler()
    observer = Observer()
    observer.schedule(handler, str(SRC_DIR), recursive=True)
    observer.start()
    
    # Inicia aplicação inicial
    global process
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC_DIR)
    env["QT_QPA_PLATFORM"] = "xcb"
    
    print("🚀 Iniciando aplicação...")
    process = subprocess.Popen(
        [sys.executable, "src/core/main.py"],
        env=env,
        cwd=SRC_DIR.parent,
    )
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Encerrando watch mode...")
        observer.stop()
        if process:
            process.terminate()
            process.wait()
        print("✅ Saído com sucesso")


if __name__ == "__main__":
    main()
