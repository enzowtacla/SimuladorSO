from dataclasses import dataclass
from typing import List
from .tarefa import Tarefa

@dataclass
class Mutex:
    id: str
    count: int = 1  # 1 = livre, 0 = bloqueado
    tarefa_dono: Tarefa = None
    tarefas_bloqueadas: List[Tarefa] = None
    
    def __post_init__(self):
        if self.tarefas_bloqueadas is None:
            self.tarefas_bloqueadas = []
    
    def lock(self, tarefa: Tarefa) -> bool:
        """Tenta travar o mutex. Retorna True se conseguiu, False se bloqueou."""
        if self.count > 0:
            self.count -= 1
            self.tarefa_dono = tarefa
            return True
        else:
            self.tarefas_bloqueadas.append(tarefa)
            return False
    
    def unlock(self, tarefa: Tarefa) -> Tarefa:
        """Libera o mutex. Retorna a próxima tarefa a ser desbloqueada, se houver."""
        if tarefa == self.tarefa_dono:
            self.count += 1
            self.tarefa_dono = None
            
            if self.tarefas_bloqueadas:
                proxima = self.tarefas_bloqueadas.pop(0)
                self.lock(proxima)  # Atribui ao próximo
                return proxima
        return None