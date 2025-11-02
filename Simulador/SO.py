from dataclasses import dataclass
from typing import List, Union
import os

from .tarefa import Tarefa, Evento
from .escalonadorFIFO import EscalonadorFIFO
from .escalonadorPrioP import EscalonadorPRIOP
from .escalonadorSRTF import EscalonadorSRTF


@dataclass
class SO:
    """Representa o sistema operacional que gerencia o escalonamento das tarefas."""
    escalonador: Union[EscalonadorFIFO, EscalonadorPRIOP, EscalonadorSRTF]
    filaTodasTarefas: List[Tarefa]  # Fila com todas as tarefas
    filaTarefasProntas: List[Tarefa]  # Fila com tarefas prontas para execução
    clock_sistema: int = 0  # Relógio do sistema
    quantum: int = 0  # Quantum para escalonadores que usam time-slicing
    ingresso_fila_prontas: bool = False  # Indica se tarefas ingressaram na fila de prontas recentemente
    tempo_executando_atual: int = 0  # Tempo que a tarefa atual está executando

    def configurar_sistema(self, filepath: str) -> None:
        """Lê o arquivo de configuração e inicializa o sistema operacional."""
        if not os.path.exists(filepath):
            raise FileNotFoundError("Arquivo de configuração não encontrado.")

        self.limpeza_sistema()
        with open(filepath, "r") as arquivo:
            linhas = arquivo.readlines()
            # Primeira linha: algoritmo_escalonamento; quantum
            tipo_escalonador, quantum = linhas[0].strip().split(";")
            self.criar_escalonador(tipo_escalonador)
            self.quantum = int(quantum)

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
                    if campo.strip(): 
                        sub_campos = campo.strip().split(":")
                        tipo = sub_campos[0]

                        if tipo == "IO":
                            sub_campos_io = sub_campos[1].split("-")
                            tempo_inicio = int(sub_campos_io[0])
                            duracao_evento = int(sub_campos_io[1])
                            evento = Evento(tipo=tipo, instante=tempo_inicio, duracao=duracao_evento)
                            lista_eventos.append(evento)
                        elif tipo == "MU" or tipo == "ML":
                            tempo_inicio = int(sub_campos[1])
                            evento = Evento(tipo=tipo, instante=tempo_inicio, duracao=None)
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

    def configurar_sistema_manual(self, tipo_escalonador: str, quantum: int, tarefas) -> None:
        """Configura o sistema operacional manualmente."""
        self.limpeza_sistema()
        self.criar_escalonador(tipo_escalonador)
        self.quantum = quantum

        # transformar tarefas em realmente uma lista de tarefas
        self.filaTodasTarefas = [Tarefa(**tarefa) for tarefa in tarefas]

    def setar_quantum(self, quantum: int) -> None:
        """Define o quantum para o sistema operacional."""
        self.quantum = quantum
    
    def setar_tarefas(self, tarefas: List[Tarefa]) -> None:
        """Define a lista de tarefas para o sistema operacional."""
        self.filaTodasTarefas = tarefas

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
    
    def remover_tarefa_pronta(self, tarefa: Tarefa) -> None:
        """Remove uma tarefa da fila de tarefas prontas."""
        if tarefa in self.filaTarefasProntas:
            self.filaTarefasProntas.remove(tarefa)

    def limpeza_sistema(self) -> None:
        """Limpa todas as filas de tarefas."""

        self.filaTodasTarefas.clear()
        self.filaTarefasProntas.clear()
        self.clock_sistema = 0

    def executar_tarefas(self) -> None:
        """Executa as tarefas na fila de tarefas prontas."""
        for tarefa in self.filaTodasTarefas:
            if not tarefa.finalizada:
                tarefa.executar()

    def primeiro_passo(self):
        self.tempo_executando_atual = 0
        self.atualizar_tarefas()
        self.atualizarFilaProntas()
        self.analisar_tarefas()

    def executar_passo(self) -> bool:
        """Executa um único passo (tick) da simulação."""
        
        if all(tarefa.finalizada for tarefa in self.filaTodasTarefas):
            return False  # Todas as tarefas foram finalizadas
    
        self.executar_tarefas() # Executa a tarefa que está rodando
        self.clock_sistema += 1 # Avança o clock

        if any(tarefa.executando for tarefa in self.filaTodasTarefas): # Incrementa o tempo de execução do quantum
            self.tempo_executando_atual += 1
        
        self.atualizar_tarefas() # Atualiza o estado das tarefas
        self.atualizarFilaProntas() # Atualiza a fila de tarefas prontas
        self.analisar_tarefas() # Analisa as tarefas para escalonamento

        if all(tarefa.finalizada for tarefa in self.filaTodasTarefas):
            return False  # Todas as tarefas foram finalizadas

        return True  # A simulação continua
    
    def atualizar_tarefas(self) -> None:
        """Atualiza o estado das tarefas com base no relógio do sistema."""

        for tarefa in self.filaTodasTarefas:
            if (tarefa.finalizada is False):
                tarefa.atualizar_estado(self.clock_sistema)

    def atualizarFilaProntas(self) -> None:
        
        for tarefa in self.filaTodasTarefas:
            if tarefa.pronta and (tarefa not in self.filaTarefasProntas):
                self.adicionar_tarefa_pronta(tarefa)
                self.ingresso_fila_prontas = True
            
            elif not tarefa.pronta and (tarefa in self.filaTarefasProntas):
                self.remover_tarefa_pronta(tarefa)
                

    def executar(self) -> None:
        """Inicia a execução do sistema operacional."""
        self.primeiro_passo()
        while not all(tarefa.finalizada for tarefa in self.filaTodasTarefas): 

            self.executar_tarefas()
            self.clock_sistema += 1

            self.tempo_executando_atual += 1
            self.atualizar_tarefas()
            self.atualizarFilaProntas()

            self.analisar_tarefas()

            self.mostrar_situacao_sistema()

    def analisar_tarefas(self) -> None:
        """Analisa as tarefas após a execução do sistema operacional."""
 
        tarefa_executando = next((tarefa for tarefa in self.filaTodasTarefas if tarefa.executando), None)

        if (len(self.filaTarefasProntas) > 0 and tarefa_executando is None) or self.ingresso_fila_prontas or (self.quantum > 0 and self.tempo_executando_atual >= self.quantum):
            for tarefa in self.filaTodasTarefas:
                if tarefa.executando:
                    tarefa.ficar_pronta()
                    self.remover_tarefa_pronta(tarefa)
                    self.adicionar_tarefa_pronta(tarefa)
                    break

            if self.ingresso_fila_prontas:
                self.ingresso_fila_prontas = False
                
            if len(self.filaTarefasProntas) > 0:
                self.escalonador.escalonar()
            self.tempo_executando_atual = 0

     

    def mostrar_situacao_sistema(self) -> None:
        """Mostra a situação atual do sistema operacional."""
        print(f"Clock = {self.clock_sistema}")
        print("Tarefas:")
        for tarefa in self.filaTodasTarefas:
            print(f"  Tarefa {tarefa.id}: Estado={tarefa.estado}, Tempo Restante={tarefa.t_restante}")
        print("-" * 40)

if __name__ == "__main__":
    so = SO(
        escalonador=None,
        filaTarefasProntas=[],
        filaTodasTarefas=[],
    )
    so.configurar_sistema("config.txt")

    for tarefa in so.filaTodasTarefas:
        print(tarefa)
        tarefa.__post_init__()

    so.executar()