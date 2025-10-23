from dataclasses import dataclass
from escalonador import Escalonador

@dataclass
class EscalonadorPRIOP(Escalonador):  # Contém as informações do escalonador
    def escalonar(self) -> None:
        """Executa o escalonamento das tarefas usando o algoritmo de Prioridade Preemptiva."""
        if self.tarefas is None or len(self.tarefas) == 0:
            return
        
        # Ordena as tarefas pela prioridade
        sorted_tarefas = sorted(self.tarefas, reverse=True, key=lambda tarefa: tarefa.prioridade)

        sorted_tarefas[0].iniciar_execucao()  # Retorna a tarefa com maior prioridade
