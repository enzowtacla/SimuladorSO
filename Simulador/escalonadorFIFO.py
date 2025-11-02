from dataclasses import dataclass
from .escalonador import Escalonador

@dataclass
class EscalonadorFIFO(Escalonador):  # Contém as informações do escalonador
    def escalonar(self) -> None:
        """Executa o escalonamento das tarefas usando o algoritmo FIFO."""
        if self.tarefas is None or len(self.tarefas) == 0:
            return
        
        # tarefas já ordenadas pq é uma fila
        self.tarefas[0].iniciar_execucao()  # Retorna a primeira tarefa da fila