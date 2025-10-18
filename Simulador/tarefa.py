from dataclasses import dataclass
from typing import List

@dataclass
class Evento:  # Contém as informações de cada evento
    tipo: str    # Tipo do evento: I/O, Mutex Lock (ML), Mutex Unlock (MU)
    instante:int # Tempo qe começo do evento
    duracao: int  # Tempo de duração do evento

@dataclass
class Tarefa:   #Contém as informações de cada tarefa
    id: str    # ID da tarefa
    cor: int   # Cor no diagrama
    ingresso:  int  # Tempo de ingresso da tarefa
    duracao:  int   # Duração da tarefa
    prioridade: int    # Prioridade da tarefa
    eventos: List[Evento] # Lista de eventos na tarefa
    estado: str = "pronta" # Estado atual da tarefa: pronta, executando, bloqueada, finalizada

    t_executado: int = 0  # Tempo já executado da tarefa
    t_restante: int = 0    # Tempo restante para ser executado

    def __post_init__(self):
        self.t_restante = self.duracao # Inicializa o tempo restante com a duração total da tarefa, roda automaticamente apos o init da dataclass  
    
    def executar(self, quantum: int) -> int:
        t_executado = min(quantum, self.t_restante) # Executa a tarefa por um quantum de tempo ou pelo tempo restantem, o que for menor
        self.t_executado += t_executado 
        self.t_restante -= t_executado

        if self.t_restante == 0:
            self.estado = "finalizada" # Sem tempo restante a tarefa terminou

        return t_executado # Retorna o tempo que foi executado
    
    @property
    def finalizada(self) -> bool:
        return self.estado == "finalizada"
    
    @property
    def bloqueada(self) -> bool:
        return self.estado == "bloqueada"
    
    @property
    def executando(self) -> bool:
        return self.estado == "executando"
    
    @property
    def pronta(self) -> bool:
        return self.estado == "pronta"