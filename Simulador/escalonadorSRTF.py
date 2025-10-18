from dataclasses import dataclass
from Simulador.escalonador import Escalonador

@dataclass
class EscalonadorSRTF(Escalonador):  # Contém as informações do escalonador
    def escalonar(self) -> None:
        """Executa o escalonamento das tarefas usando o algoritmo SRTF."""
        if self.tarefas is None or len(self.tarefas) == 0:
            return

        # Ordena as tarefas pelo tempo restante]
        sorted_tarefas = sorted(self.tarefas, key=lambda tarefa: tarefa.t_restante)

        return sorted_tarefas.pop(0)  # Retorna a tarefa com menor tempo restante