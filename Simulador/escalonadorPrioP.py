from dataclasses import dataclass
from .escalonador import Escalonador

# implementação do escalonador de Prioridade Preemptiva
@dataclass
class EscalonadorPRIOP(Escalonador):

    def escalonar(self) -> None:
        """Executa o escalonamento das tarefas usando o algoritmo de Prioridade Preemptiva."""
        if self.tarefas is None or len(self.tarefas) == 0:
            return
        
        # Ordena as tarefas pela prioridade -- reverse = True para maior prioridade primeiro
        sorted_tarefas = sorted(self.tarefas, reverse=True, key=lambda tarefa: tarefa.prioridade)

        sorted_tarefas[0].iniciar_execucao()  # Retorna a tarefa com maior prioridade
