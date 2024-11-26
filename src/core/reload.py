import os
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PySide6.QtCore import Signal, QObject, QCoreApplication

# Classe para gerenciar os sinais e recarregar a interface
class ReloadSignal(QObject):
    reload_signal = Signal()  

    def __init__(self):
        super().__init__()

    def reload_app(self):
        # Fecha a aplicação e reinicia
        print("Reiniciando a aplicação...")
        QCoreApplication.quit()
        os.execv(sys.executable, ['python'] + sys.argv)

# Classe de monitoramento de arquivos
class ReloadHandler(FileSystemEventHandler):
    def __init__(self, reload_signal):
        self.reload_signal = reload_signal

    def on_modified(self, event):
        if event.src_path.endswith('.py'):  
            print("Mudança detectada! Recarregando...")
            self.reload_signal.reload_signal.emit()

# Função para configurar o monitoramento
def setup_reload_signal():
    reload_signal = ReloadSignal()
    return reload_signal
