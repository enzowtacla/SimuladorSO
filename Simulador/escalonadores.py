from dataclasses import dataclass
from typing import List
from abc import ABC
from abc import abstractmethod
from .tarefa import Tarefa

lista_escalonadores = ["FCFS", "PRIOP", "SRTF"]

# Classe base para escalonadores
@dataclass
class Escalonador(ABC):
    tarefas: List[Tarefa]   # Lista de tarefas a serem escalonadas
    tarefa_atual: Tarefa = None  # Tarefa atualmente em execução
    # método abstrato para escalonar -- chamada do mesmo método para todos os escalonadores
    @abstractmethod
    def escalonar(self) -> None:
        """Executa o escalonamento das tarefas."""
        raise NotImplementedError
    
    # criação de escalonador específicos abaixo
    @staticmethod
    def criar_escalonador(tipo: str, tarefas: List[Tarefa]) -> 'Escalonador':
        """Fábrica para criar escalonadores específicos com base no tipo."""
        if tipo == "FCFS":
            return EscalonadorFCFS(tarefas)
        elif tipo == "PRIOP":
            return EscalonadorPRIOP(tarefas)
        elif tipo == "SRTF":
            return EscalonadorSRTF(tarefas)
        else:
            raise ValueError("Tipo de escalonador desconhecido.")   

    def escolha_em_casos_empate(self) -> None:
        """Define a estratégia de escolha em casos de empate."""
        pass

@dataclass
class EscalonadorFCFS(Escalonador):

    def escalonar(self) -> None:
        """Executa o escalonamento das tarefas usando o algoritmo FCFS."""
        if self.tarefas is None or len(self.tarefas) == 0:
            return
        
        # tarefas já ordenadas pq é uma fila
        self.tarefas[0].iniciar_execucao()  # Retorna a primeira tarefa da fila


# implementação do escalonador de Prioridade Preemptiva
@dataclass
class EscalonadorPRIOP(Escalonador):

    def escalonar(self) -> None:
        """Executa o escalonamento das tarefas usando o algoritmo de Prioridade Preemptiva."""
        if self.tarefas is None or len(self.tarefas) == 0:
            return
        # Ordena as tarefas pela prioridade -- reverse = True para maior prioridade primeiro
        tarefa_maior_prio = max(self.tarefas, key=lambda tarefa: tarefa.prioridade)

        tarefa_maior_prio.iniciar_execucao()  # Retorna a tarefa com maior prioridade

# implementação do escalonador SRTF
@dataclass
class EscalonadorSRTF(Escalonador):
    def escalonar(self) -> None:
        """Executa o escalonamento das tarefas usando o algoritmo SRTF."""
        if self.tarefas is None or len(self.tarefas) == 0:
            return

        # Ordena as tarefas pelo tempo restante
        tarefa_menor_tempo = min(self.tarefas, key=lambda tarefa: tarefa.t_restante)

        tarefa_menor_tempo.iniciar_execucao()  # Retorna a tarefa com menor tempo restante