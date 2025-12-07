# arquivo: simulador/__init__.py
from .interface import Interface
from .SO import SO
from .tarefa import Tarefa
from .eventos import Evento, EventoIO, EventoMutexLock, EventoMutexUnlock
from .escalonadores import *
from .modalConfigManual import ModalConfigManual
from .modalTarefa import ModalTarefas
from .modalEvento import ModalEvent
from .modalAjuda import ModalAjuda
from .cores import CORES_TAREFAS, COR_TAREFA_NAO_EXECUTANDO, get_cor_nome, get_cor_hex, get_lista_cores_para_combobox, extrair_id_cor_do_texto

# Se você criar o arquivo mutex.py, adicione:
# from .mutex import Mutex

__all__ = [
    'Interface', 'SO', 'Tarefa', 'Evento', 'EventoIO', 'EventoMutexLock', 'EventoMutexUnlock',
    'EscalonadorFCFS', 'EscalonadorPRIOP', 'EscalonadorSRTF', 'EscalonadorPRIOPEnv',
    'ModalConfigManual', 'ModalTarefas', 'ModalEvent', 'ModalAjuda',
    'CORES_TAREFAS', 'COR_TAREFA_NAO_EXECUTANDO', 'get_cor_nome', 'get_cor_hex',
    'get_lista_cores_para_combobox', 'extrair_id_cor_do_texto'
]