from dataclasses import dataclass
from typing import List
from abc import ABC
from abc import abstractmethod
from .tarefa import Tarefa

# Classe base para escalonadores
@dataclass
class Escalonador(ABC):
    tarefas: List[Tarefa]   # Lista de tarefas a serem escalonadas

    # método abstrato para escalonar -- chamada do mesmo método para todos os escalonadores
    @abstractmethod
    def escalonar(self) -> None:
        """Executa o escalonamento das tarefas."""
        raise NotImplementedError