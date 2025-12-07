from dataclasses import dataclass
from typing import List
from .eventos import *

@dataclass
class Tarefa:   #Contém as informações de cada tarefa
    id: str    # ID da tarefa
    cor: str   # Cor no diagrama
    ingresso:  int  # Tempo de ingresso da tarefa
    duracao:  int   # Duração da tarefa
    prioridade_estatica: int    # Prioridade da tarefa
    prioridade_dinamica: int  # Prioridade dinâmica (pode ser alterada durante a execução)
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
        self.prioridade_dinamica = self.prioridade_estatica
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
        elif self.bloqueada and self.evento_bloqueio_atual:
            self.evento_bloqueio_atual.tratar_evento()
    ''' # se está bloqueada por tempo maior ou igual à duração do bloqueio, ela fica pronta
            if self.t_bloqueado >= self.evento_bloqueio_atual.duracao:
                self.ficar_pronta()
                self.t_bloqueado = 0
            # senão, incrementa o tempo bloqueado
            else:
                self.t_bloqueado += 1 '''
    # se a tarefa está executando, realiza as seguintes operações
    def executar(self) -> None:
        if self.executando:
            for evento in self.eventos:
                if evento.instante == self.t_executado:
                    evento.tratar_evento()
                    self.bloquear()
                    self.evento_bloqueio_atual = evento
                    break  
            # decrementa o tempo restante e incrementa o tempo executado
            self.t_restante -= 1
            self.t_executado += 1

    def resetar_prioridade_dinamica(self) -> None:
        """Reseta a prioridade dinâmica para a prioridade estática."""
        self.prioridade_dinamica = self.prioridade_estatica

    def adicionar_evento(self, campo, so) -> None:
        """Adiciona um evento à lista de eventos da tarefa."""
        self.eventos.append(Evento.criar_evento(campo=campo, sistema=so))

    def adicionar_evento(self, evento, sistema) -> None:
        """Adiciona um evento à lista de eventos da tarefa."""
        self.eventos.append(Evento.criar_evento(evento=evento, sistema=sistema))

    def limpar_eventos(self) -> None:
        """Limpa a lista de eventos da tarefa."""
        self.eventos = []

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