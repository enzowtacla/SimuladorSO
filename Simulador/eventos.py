from dataclasses import dataclass
lista_eventos_tipos = ["IO", "ML", "MU"]  
mapa_tipos_display = {
            "IO": "I/O", 
            "ML": "Mutex Lock", 
            "MU": "Mutex Unlock"
        }

mapa_tipos_reverso = {
                    "IO": "I/O", 
                    "ML": "Mutex Lock", 
                    "MU": "Mutex Unlock"
                } # mapeia abreviações para nomes completos
@dataclass
class Evento:  # Contém as informações de cada evento
    tipo: str    # Tipo do evento: I/O, Mutex Lock (ML), Mutex Unlock (MU) -- maioria ainda não tratados
    instante:int # Tempo qe começo do evento
    duracao: int  # Tempo de duração do evento