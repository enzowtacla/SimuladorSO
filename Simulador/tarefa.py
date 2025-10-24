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
    evento_bloqueio_atual: Evento = None  # Evento que causou o bloqueio atual
    estado: str = "aguardando" # Estado atual da tarefa: pronta, executando, bloqueada, finalizada

    t_executado: int = 0  # Tempo já executado da tarefa
    t_restante: int = 0    # Tempo restante para ser executado
    t_bloqueado: int = 0    # Tempo que a tarefa está bloqueada

    def __post_init__(self):
        self.t_restante = self.duracao
        if self.ingresso == 0:
            self.estado = "pronta"
        else:
            self.estado = "aguardando"
    
    def atualizar_estado(self, clock: int) -> None:
        if self.t_restante == 0:
            self.finalizar()
        elif self.ingresso == clock and self.estado == "aguardando":
            self.ficar_pronta()
        elif self.bloqueada:

            if self.t_bloqueado >= self.evento_bloqueio_atual.duracao:
                self.ficar_pronta()
                self.t_bloqueado = 0
                print(f"Tarefa {self.id} desbloqueada após I/O.")
            self.t_bloqueado += 1 
            print(f"Tarefa {self.id} está bloqueada por {self.t_bloqueado} unidades de tempo.")

    def executar(self) -> None:
        if self.executando:
            self.t_restante -= 1
            self.t_executado += 1
            for evento in self.eventos:
                if evento.tipo == "IO" and evento.instante == self.t_executado:
                    self.bloquear()
                    self.evento_bloqueio_atual = evento
                    break  

    def bloquear(self) -> None:
        self.estado = "bloqueada"

    def ficar_pronta(self) -> None:
        self.estado = "pronta"
    
    def iniciar_execucao(self) -> None:
        self.estado = "executando"

    def finalizar(self) -> None:
        self.estado = "finalizada"

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
    
    @property
    def aguardando(self) -> bool:
        return self.estado == "aguardando"