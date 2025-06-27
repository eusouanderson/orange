import subprocess
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

START_SCRIPT = './start.sh'
WATCH_DIR = Path(__file__).resolve().parent.parent / 'src'


class ReloadHandler(FileSystemEventHandler):
    process = None

    def on_any_event(self, event):
        if event.is_directory or event.event_type == 'modified':
            print(f'🔄 Alteração detectada em: {event.src_path}')
            self.restart()

    def restart(self):
        if self.process:
            print('🛑 Parando o processo anterior...')
            self.process.kill()
        print(f'🚀 Executando {START_SCRIPT}...')
        self.process = subprocess.Popen(['bash', START_SCRIPT])
        print('✅ Processo reiniciado com sucesso.')


if __name__ == '__main__':
    print(f'👀 Observando mudanças em: {WATCH_DIR}')
    event_handler = ReloadHandler()
    observer = Observer()
    observer.schedule(event_handler, str(WATCH_DIR), recursive=True)
    observer.start()
    try:
        while True:
            pass  # Mantém o script vivo
    except KeyboardInterrupt:
        observer.stop()
        if event_handler.process:
            event_handler.process.kill()
    observer.join()
