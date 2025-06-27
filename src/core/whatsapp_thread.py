import logging
import re
import time

import pyautogui
import pywhatkit
from PyQt6.QtCore import QThread, pyqtSignal


class WhatsAppSenderThread(QThread):
    update_progress = pyqtSignal(int, str, bool)
    log_message = pyqtSignal(str, str)
    finished = pyqtSignal(bool, str)

    def __init__(
        self,
        phone_numbers,
        message,
        delay_seconds=30,
        agendar=False,
        hora=None,
        minuto=None,
    ):
        super().__init__()
        self.phone_numbers = phone_numbers
        self.message = message
        self.delay_seconds = delay_seconds
        self.agendar = agendar
        self.hora = hora
        self.minuto = minuto
        self._is_running = True
        self.logger = logging.getLogger(__name__)

    def formatar_numero_whatsapp(self, numero: str) -> str:
        """Formata o número para o padrão internacional do WhatsApp (+55...)"""
        numero = re.sub(r'\D', '', numero)
        if not numero.startswith('55'):
            numero = '55' + numero
        return f'+{numero}'

    # pylint: disable=PLR6301
    def pressionar_enter_apos_envio(self, delay: int = 1):
        """Espera alguns segundos e pressiona Enter"""
        time.sleep(delay)
        pyautogui.press('enter')

    def run(self):
        success = False
        error_message = ''
        sent_count = 0
        total = len(self.phone_numbers)

        self.log_message.emit(f'Iniciando envio para {total} contatos', 'info')
        self.logger.info(f'Iniciando envio para {total} contatos')

        try:
            for i, phone in enumerate(self.phone_numbers):
                if not self._is_running:
                    self.log_message.emit(
                        'Envio cancelado pelo usuário', 'warning'
                    )
                    break

                numero_formatado = self.formatar_numero_whatsapp(phone)
                self.update_progress.emit(
                    i + 1, f'Enviando para {numero_formatado}', False
                )
                self.log_message.emit(
                    f'Preparando envio para {numero_formatado}', 'info'
                )

                try:
                    kwargs = {
                        'phone_no': numero_formatado,
                        'message': self.message,
                        'wait_time': self.delay_seconds,
                        'tab_close': False,
                        'close_time': 5,
                    }

                    if (
                        self.agendar
                        and self.hora is not None
                        and self.minuto is not None
                    ):
                        self.log_message.emit(
                            f'Agendando mensagem para {self.hora:02d}:{
                                self.minuto:02d
                            }',
                            'info',
                        )
                        pywhatkit.sendwhatmsg(
                            time_hour=self.hora, time_min=self.minuto, **kwargs
                        )
                    else:
                        self.log_message.emit(
                            'Enviando mensagem instantânea', 'info'
                        )
                        pywhatkit.sendwhatmsg_instantly(**kwargs)
                        self.pressionar_enter_apos_envio()
                        time.sleep(2)
                        pyautogui.hotkey('ctrl', 'w')  # Fecha a aba

                    sent_count += 1
                    success_msg = (
                        f'Sucesso: mensagem enviada para {numero_formatado}'
                    )
                    self.update_progress.emit(i + 1, success_msg, True)
                    self.log_message.emit(success_msg, 'success')
                    time.sleep(2)

                except Exception as e:
                    error_msg = f'Erro ao enviar para {phone}: {str(e)}'
                    self.update_progress.emit(i + 1, error_msg, False)
                    self.log_message.emit(error_msg, 'error')
                    self.logger.error(error_msg)
                    continue

            success = True
            result_msg = (
                f'Enviadas {sent_count} de {total} mensagens com sucesso'
            )
            self.log_message.emit(result_msg, 'success')
            self.logger.info(result_msg)
        except Exception as e:
            error_message = f'Erro crítico: {str(e)}'
            self.log_message.emit(error_message, 'error')
            self.logger.error(error_message)
        finally:
            self.finished.emit(
                success, error_message if not success else result_msg
            )

    def stop(self):
        self._is_running = False
        self.log_message.emit('Parando thread de envio...', 'warning')
