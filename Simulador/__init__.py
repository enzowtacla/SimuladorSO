# arquivo utilizado para definir o que será importado ao importar o pacote Simulador
from .interface import Interface
from .SO import SO
from .tarefa import Tarefa, Evento
from .escalonadores import *
from .modalConfigManual import ModalConfigManual
from .modalTarefa import ModalTarefas
from .modalEvento import ModalEvent
from .modalAjuda import ModalAjuda
from .cores import CORES_TAREFAS, COR_TAREFA_NAO_EXECUTANDO, get_cor_nome, get_cor_hex, get_lista_cores_para_combobox, extrair_id_cor_do_texto
__all__ = ['Interface', 'SO', 'Tarefa', 'Evento', 'EscalonadorFCFS', 'EscalonadorPRIOP', 'EscalonadorSRTF', 'ModalConfigManual', 'ModalTarefas', 'ModalEvent', 'ModalAjuda', 'CORES_TAREFAS', 'COR_TAREFA_NAO_EXECUTANDO', 'get_cor_nome', 'get_cor_hex', 'get_lista_cores_para_combobox', 'extrair_id_cor_do_texto']