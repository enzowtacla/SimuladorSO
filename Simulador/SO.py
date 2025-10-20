from dataclasses import dataclass
from typing import List, Any, Union
import os

from Simulador.tarefa import Tarefa, Evento
from Simulador.escalonadorFIFO import EscalonadorFIFO
from Simulador.escalonadorPrioP import EscalonadorPRIOP
from Simulador.escalonadorSRTF import EscalonadorSRTF


@dataclass
class SO:
    """Representa o sistema operacional que gerencia o escalonamento das tarefas."""
    escalonador: Union[EscalonadorFIFO, EscalonadorPRIOP, EscalonadorSRTF]
    filaTarefasProntas: List[Tarefa]  # Fila de tarefas prontas para execução
    filaTodasTarefas: List[Tarefa]  # Fila com todas as tarefas
    tarefaExecutando: Tarefa  # Tarefa atualmente em execução

    def configurar_sistema(self) -> None:
        """Lê o arquivo de configuração e inicializa o sistema operacional."""
        if not os.path.exists("config.txt"):
            raise FileNotFoundError("Arquivo de configuração não encontrado.")

        with open("config.txt", "r") as arquivo:
            linhas = arquivo.readlines()
            # Primeira linha: algoritmo_escalonamento; quantum
            tipo_escalonador, quantum = linhas[0].strip().split(";")
            self.criar_escalonador(tipo_escalonador)
            lista_eventos: List[Evento] = []
            #próximas linhas são as tarefas
            for linha in linhas[1:]:
                campos = linha.strip().split(";")
                id = campos[0]
                cor = int(campos[1])
                ingresso = int(campos[2])
                duracao = int(campos[3])
                prioridade = int(campos[4])

                lista_eventos: List[Evento] = []

                for campo in campos[5:]:
                    sub_campos = campo.strip().split(":")
                    tipo = sub_campos[0]

                    if tipo == "IO":
                        sub_campos_io = sub_campos[1].split("-")
                        tempo_inicio = int(sub_campos_io[0])
                        duracao = int(sub_campos_io[1])
                    elif tipo == "MU" or tipo == "ML": 
                        tempo_inicio = int(sub_campos[1])
                        duracao = None

                    instante = tempo_inicio + ingresso

                    evento = Evento(tipo=tipo, instante=instante, duracao=duracao) 
                    lista_eventos.append(evento)

                tarefa = Tarefa(
                    id=id,
                    cor=int(cor),
                    ingresso=int(ingresso),
                    duracao=int(duracao),
                    prioridade=int(prioridade),
                    eventos=lista_eventos,
                )
                self.adicionar_tarefa(tarefa)

    def criar_escalonador(self, tipo: str) -> None:
        """Cria o escalonador apropriado com base no tipo especificado."""
        if tipo == "FCFS":
            self.escalonador = EscalonadorFIFO(tarefas=self.filaTarefasProntas)
        elif tipo == "PRIOP":
            self.escalonador = EscalonadorPRIOP(tarefas=self.filaTarefasProntas)
        elif tipo == "SRTF":
            self.escalonador = EscalonadorSRTF(tarefas=self.filaTarefasProntas)
        else:
            raise ValueError("Tipo de escalonador desconhecido.")

    def adicionar_tarefa(self, tarefa: Tarefa) -> None:
        """Adiciona uma tarefa à fila de tarefas geral"""
        self.filaTodasTarefas.append(tarefa)

    def adicionar_tarefa_pronta(self, tarefa: Tarefa) -> None:
        """Adiciona uma tarefa à fila de tarefas prontas."""
        self.filaTarefasProntas.append(tarefa)

if __name__ == "__main__":
    so = SO(
        escalonador=None,
        filaTarefasProntas=[],
        filaTodasTarefas=[],
        tarefaExecutando=None
    )
    so.configurar_sistema()

    for tarefa in so.filaTodasTarefas:
        print(tarefa)