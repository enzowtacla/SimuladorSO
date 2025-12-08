from dataclasses import dataclass
from abc import ABC, abstractmethod

lista_eventos_tipos = ["I/O", "Mutex Lock", "Mutex Unlock"]  
mapa_tipos_display = {
            "IO": "I/O", 
            "ML": "Mutex Lock", 
            "MU": "Mutex Unlock"
        }

mapa_tipos_reverso = {
                    "I/O": "IO", 
                    "Mutex Lock": "ML", 
                    "Mutex Unlock": "MU"
                } # mapeia abreviações para nomes completos
@dataclass
class Evento:  # Contém as informações de cada evento
    tipo: str    # Tipo do evento: I/O, Mutex Lock (ML), Mutex Unlock (MU) -- maioria ainda não tratados
    instante:int # Tempo qe começo do evento
    estado: str = "pendente"  # Estado do evento: pendente, em andamento, concluído
    sistema: 'SO' = None   # Referência ao sistema operacional para manipulação de recursos
    @staticmethod
    def criar_evento_campo(campo, sistema) -> 'Evento':
        """Cria um evento a partir de uma string de campo."""
        sub_campos = campo.strip().split(":") # separa os subcampos do evento
        tipo = sub_campos[0] # tipo do evento

            # se for I/O, possui tempo de início e duração
        if tipo == "IO":
            sub_campos_io = sub_campos[1].split("-") # separa tempo de início e duração
            tempo_inicio = int(sub_campos_io[0])
            duracao_evento = int(sub_campos_io[1])
            evento = EventoIO(tipo=tipo, instante=tempo_inicio, duracao=duracao_evento, sistema=sistema) # cria o evento
        # se for MU ou ML, possui apenas tempo de início
        elif tipo[0:2] == "MU" or tipo[0:2] == "ML":
            tempo_inicio = int(sub_campos[1])
            evento = EventoMutex(tipo=tipo[0:2], mutex_id=tipo[2:], instante=tempo_inicio, sistema=sistema) # cria o evento

        return evento
    
    @staticmethod
    def criar_evento(evento, sistema) -> 'Evento':
        if evento["tipo_evento"] == "IO":
            return EventoIO(tipo=evento["tipo_evento"], instante=evento["instante"], duracao=evento["duracao"], sistema=sistema)
        elif evento["tipo_evento"] == "ML":
            return EventoMutexLock(tipo=evento["tipo_evento"], mutex_id=evento["mutex_id"], instante=evento["instante"], sistema=sistema)
        elif evento["tipo_evento"] == "MU":
            return EventoMutexUnlock(tipo=evento["tipo_evento"], mutex_id=evento["mutex_id"], instante=evento["instante"], sistema=sistema)

    @abstractmethod
    def tratar_evento(self):
        pass

    @property
    def pendente(self) -> bool:
        return self.estado == "pendente"
    @property
    def em_andamento(self) -> bool:
        return self.estado == "em andamento"
    @property
    def concluido(self) -> bool:
        return self.estado == "concluído"

@dataclass
class EventoIO(Evento):
    duracao: int = 0  # Duração do evento de I/O
    dispositivo: str = ""  # Dispositivo de I/O associado ao evento
    tempo_restante: int = 0  # Tempo restante do evento
    def __post_init__(self):
        self.tipo = "IO"
        self.tempo_restante = self.duracao
    
    def tratar_evento(self):
        if self.tempo_restante >= self.duracao and self.pendente:
            self.estado = "em andamento"
            self.sistema.tratar_req_inicio_io(self)


@dataclass
class EventoMutex(Evento):
    mutex_id: str = ""  # ID do mutex associado ao evento

    @staticmethod
    def criarEventoMutex(tipo: str, mutex_id: str, instante: int, sistema) -> 'EventoMutex':
        if tipo == "ML":
            evento = EventoMutexLock(tipo=tipo, mutex_id=mutex_id, instante=instante, sistema=sistema)
        elif tipo == "MU":
            evento = EventoMutexUnlock(tipo=tipo, mutex_id=mutex_id, instante=instante, sistema=sistema)
        return evento

    def tratar_evento(self):
        pass

@dataclass
class EventoMutexLock(EventoMutex):
    def __post_init__(self):
        self.tipo = "ML"
    def tratar_evento(self):
        if self.sistema:
            self.sistema.tratar_req_mutex_lock(self)

@dataclass
class EventoMutexUnlock(EventoMutex):
    def __post_init__(self):
        self.tipo = "MU"
    def tratar_evento(self):
        if self.sistema:
            self.sistema.tratar_req_mutex_unlock(self)