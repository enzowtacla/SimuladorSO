from dataclasses import dataclass
from typing import List

@dataclass
class Evento:  # Contém as informações de cada evento
    tipo: str    # Tipo do evento: I/O, Mutex Lock (ML), Mutex Unlock (MU) -- maioria ainda não tratados
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

    # inicializa tempo restante e estado da tarefa
    def __post_init__(self):
        # Inicializa o tempo restante com a duração total
        self.t_restante = self.duracao
        # se a tarefa já ingressa no tempo 0, ela fica pronta imediatamente
        # do contrario, fica aguardando seu ingresso
        if self.ingresso == 0:
            self.estado = "pronta"
        else:
            self.estado = "aguardando"
    
    # atualiza o estado da tarefa a cada tick do relógio
    def atualizar_estado(self, clock: int) -> None:
        # se o tempo restante for 0, finaliza a tarefa
        if self.t_restante == 0:
            self.finalizar()
        # se o tempo de ingresso for igual ao clock atual e a tarefa estiver aguardando, ela fica pronta
        elif self.ingresso == clock and self.estado == "aguardando":
            self.ficar_pronta()

        # se a tarefa estava bloqueada, verifica se já terminou o bloqueio
        elif self.bloqueada:

            # se está bloqueada por tempo maior ou igual à duração do bloqueio, ela fica pronta
            if self.t_bloqueado >= self.evento_bloqueio_atual.duracao:
                self.ficar_pronta()
                self.t_bloqueado = 0
            # senão, incrementa o tempo bloqueado
            else:
                self.t_bloqueado += 1 

    # se a tarefa está executando, realiza as seguintes operações
    def executar(self) -> None:
        if self.executando:
            # decrementa o tempo restante e incrementa o tempo executado
            self.t_restante -= 1
            self.t_executado += 1
            # verifica se há algum evento de I/O a ser iniciado
            for evento in self.eventos:
                # se houver um evento de I/O no instante atual, bloqueia a tarefa
                if evento.tipo == "IO" and evento.instante == self.t_executado:
                    self.bloquear()
                    # armazenar o evento de bloqueio atual
                    self.evento_bloqueio_atual = evento
                    break  

    # métodos para alterar o estado da tarefa
    def bloquear(self) -> None:
        self.estado = "bloqueada"

    def ficar_pronta(self) -> None:
        self.estado = "pronta"
    
    def iniciar_execucao(self) -> None:
        self.estado = "executando"

    def finalizar(self) -> None:
        self.estado = "finalizada"

    # propriedades para verificar o estado da tarefa -- retorna se a tarefa está em determinado estado
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