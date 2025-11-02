from dataclasses import dataclass
from typing import List
from abc import ABC
from abc import abstractmethod
from .tarefa import Tarefa

@dataclass
class Escalonador(ABC):  # Contém as informações do escalonador
    tarefas: List[Tarefa]   # Lista de tarefas a serem escalonadas

    @abstractmethod
    def escalonar(self) -> None:
        """Executa o escalonamento das tarefas."""
        raise NotImplementedError