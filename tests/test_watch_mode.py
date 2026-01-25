import subprocess
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from scripts import watch


class TestSourceChangeHandler(unittest.TestCase):
    """Testes para SourceChangeHandler do watch mode."""

    def setUp(self):
        """Reset module-level process before each test."""
        watch.process = None

    def test_ignora_diretorios(self):
        """Verifica se ignora modificações em diretórios."""
        handler = watch.SourceChangeHandler()
        event = MagicMock()
        event.is_directory = True
        event.src_path = "/home/bob/orange/src/components"

        with patch.object(handler, "_restart_app") as mock_restart:
            handler.on_modified(event)
            mock_restart.assert_not_called()

    def test_ignora_arquivos_nao_python(self):
        """Verifica se ignora arquivos não-Python."""
        handler = watch.SourceChangeHandler()
        event = MagicMock()
        event.is_directory = False
        event.src_path = "/home/bob/orange/src/utils.txt"

        with patch.object(handler, "_restart_app") as mock_restart:
            handler.on_modified(event)
            mock_restart.assert_not_called()

    def test_ignora_diretorios_ignorados(self):
        """Verifica se ignora diretórios como __pycache__ e .git."""
        handler = watch.SourceChangeHandler()
        
        for dirname in ["__pycache__", ".pytest_cache", ".git"]:
            event = MagicMock()
            event.is_directory = False
            event.src_path = f"/home/bob/orange/src/{dirname}/module.py"

            with patch.object(handler, "_restart_app") as mock_restart:
                handler.on_modified(event)
                mock_restart.assert_not_called()

    def test_recarrega_para_python_files(self):
        """Verifica se dispara reinicialização para arquivos Python."""
        handler = watch.SourceChangeHandler()
        event = MagicMock()
        event.is_directory = False
        event.src_path = "/home/bob/orange/src/core/main.py"

        with patch.object(handler, "_restart_app") as mock_restart:
            handler.on_modified(event)
            mock_restart.assert_called_once()

    @patch("scripts.watch.subprocess.Popen")
    def test_restart_app_termina_processo_anterior(self, mock_popen):
        """Verifica se encerra processo anterior antes de iniciar novo."""
        handler = watch.SourceChangeHandler()

        # Mock do processo anterior
        mock_process = MagicMock()
        mock_process.wait.return_value = None
        watch.process = mock_process

        mock_new_process = MagicMock()
        mock_popen.return_value = mock_new_process

        handler._restart_app()

        # Verifica se chamou terminate no processo anterior
        mock_process.terminate.assert_called_once()
        # Verifica se criou novo processo
        mock_popen.assert_called_once()

    @patch("scripts.watch.subprocess.Popen")
    def test_restart_app_cria_novo_processo(self, mock_popen):
        """Verifica se cria novo processo subprocess."""
        handler = watch.SourceChangeHandler()
        watch.process = None

        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        handler._restart_app()

        # Verifica se criou novo processo
        mock_popen.assert_called_once()
        # Verifica se salvou no módulo watch
        assert watch.process == mock_process

    @patch("scripts.watch.subprocess.Popen")
    def test_kill_processo_se_timeout(self, mock_popen):
        """Verifica se mata processo se timeout ao terminate."""
        handler = watch.SourceChangeHandler()

        mock_process = MagicMock()
        mock_process.wait.side_effect = subprocess.TimeoutExpired("cmd", 3)
        watch.process = mock_process

        mock_new_process = MagicMock()
        mock_popen.return_value = mock_new_process

        handler._restart_app()

        # Verifica se chamou kill após timeout
        mock_process.kill.assert_called_once()


class TestWatchModuleConfiguration(unittest.TestCase):
    """Testes para configuração do módulo watch."""

    def test_src_dir_exists(self):
        """Verifica se SRC_DIR aponta para diretório válido."""
        assert watch.SRC_DIR.exists()
        assert watch.SRC_DIR.is_dir()

    def test_extensions_contains_py(self):
        """Verifica se EXTENSIONS inclui .py."""
        assert ".py" in watch.EXTENSIONS

    def test_ignore_dirs_configured(self):
        """Verifica se IGNORE_DIRS está configurado corretamente."""
        assert "__pycache__" in watch.IGNORE_DIRS
        assert ".git" in watch.IGNORE_DIRS
        assert ".pytest_cache" in watch.IGNORE_DIRS

    def test_src_dir_is_src_folder(self):
        """Verifica se SRC_DIR aponta para ./src."""
        assert watch.SRC_DIR.name == "src"
        assert watch.SRC_DIR.exists()
