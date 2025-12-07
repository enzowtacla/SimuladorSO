from dataclasses import dataclass
from typing import List, Union
import os

from .tarefa import Tarefa, Evento
from .escalonadores import *

# a classe do sistema operacional
@dataclass
class SO:
    """Representa o sistema operacional que gerencia o escalonamento das tarefas."""
    escalonador: Union[EscalonadorFIFO, EscalonadorPRIOP, EscalonadorSRTF] # Escalonador usado pelo sistema operacional -- adicionar os tipos aqui quando criar mais
    filaTodasTarefas: List[Tarefa]  # Fila com todas as tarefas
    filaTarefasProntas: List[Tarefa]  # Fila com tarefas prontas para execução
    clock_sistema: int = 0  # Relógio do sistema
    quantum: int = 0  # Quantum para escalonadores que usam time-slicing
    ingresso_fila_prontas: bool = False  # Indica se tarefas ingressaram na fila de prontas recentemente
    tempo_executando_atual: int = 0  # Tempo que a tarefa atual está executando
    nome_tipo_escalonador: str = "" # guarda o nome do tipo de escalonador usado atualmente

    # configura o sistema operacional a partir de um arquivo de configuração
    def configurar_sistema(self, filepath: str) -> None:
        """Lê o arquivo de configuração e inicializa o sistema operacional."""
        # verifica se o arquivo existe, se não, lança um erro
        if not os.path.exists(filepath):
            raise FileNotFoundError("Arquivo de configuração não encontrado.")

        # limpa o sistema antes de configurar
        self.limpeza_sistema()

        # verifica o conteúdo do arquivo com base na estrutura esperada
        with open(filepath, "r") as arquivo:
            linhas = arquivo.readlines()
            # Primeira linha: algoritmo_escalonamento; quantum
            tipo_escalonador, quantum = linhas[0].strip().split(";")
            self.criar_escalonador(tipo_escalonador)
            self.quantum = int(quantum)

            #próximas linhas são as tarefas, então lê cada linha e cria as tarefas com base no modelo
            for linha in linhas[1:]:
                campos = linha.strip().split(";") # separa os campos da linha
                id = campos[0]
                cor = int(campos[1])
                ingresso = int(campos[2])
                duracao = int(campos[3])
                prioridade = int(campos[4])
                
                # inicializa a lista de eventos
                lista_eventos: List[Evento] = []

                # lê os eventos, se houver
                for campo in campos[5:]:
                    if campo.strip(): 
                        sub_campos = campo.strip().split(":") # separa os subcampos do evento
                        tipo = sub_campos[0] # tipo do evento

                        # se for I/O, possui tempo de início e duração
                        if tipo == "IO":
                            sub_campos_io = sub_campos[1].split("-") # separa tempo de início e duração
                            tempo_inicio = int(sub_campos_io[0])
                            duracao_evento = int(sub_campos_io[1])
                            evento = Evento(tipo=tipo, instante=tempo_inicio, duracao=duracao_evento) # cria o evento
                            lista_eventos.append(evento) # adiciona o evento à lista
                        # se for MU ou ML, possui apenas tempo de início
                        elif tipo == "MU" or tipo == "ML":
                            tempo_inicio = int(sub_campos[1])
                            evento = Evento(tipo=tipo, instante=tempo_inicio, duracao=0) # cria o evento
                            lista_eventos.append(evento) # adiciona o evento à lista

                # cria a tarefa com os dados lidos
                tarefa = Tarefa(
                    id=id,
                    cor=int(cor),
                    ingresso=int(ingresso),
                    duracao=int(duracao),
                    prioridade=int(prioridade),
                    eventos=lista_eventos,
                )

                # adiciona a tarefa à fila de todas as tarefas
                self.adicionar_tarefa(tarefa)
    
    def configurar_sistem_manual(self, tipo_escalonador: str, quantum: int, tarefas) -> None:
        """Configura o sistema operacional manualmente."""
        self.limpeza_sistema() # limpa o sistema antes de configurar
        self.criar_escalonador(tipo_escalonador) # cria o escalonador
        self.setar_quantum(quantum) # define o quantum

        # transformar tarefas em realmente uma lista de tarefas e eventos em reais eventos
        tarefas_convertidas: List[Tarefa] = [] # inicializa a lista de tarefas convertidas
        for tarefa in tarefas:
            eventos_convertidos: List[Evento] = [] # inicializa a lista de eventos convertidos
            # percorre os eventos da tarefa e cria objetos Evento
            for evento in tarefa.get('eventos', []):
                evento_convertido = Evento(evento['tipo_evento'], evento['instante'], evento.get('duracao')) # cria o evento
                eventos_convertidos.append(evento_convertido) # adiciona o evento à lista
            # cria o objeto Tarefa com os dados convertidos
            tarefa_convertida = Tarefa (
                id=tarefa['id'],
                cor=tarefa['cor'],
                ingresso=tarefa['ingresso'],
                duracao=tarefa['duracao'],
                prioridade=tarefa['prioridade'],
                eventos=eventos_convertidos)
            tarefas_convertidas.append(tarefa_convertida) # adiciona a tarefa convertida à lista
        self.setar_tarefas(tarefas_convertidas) # define a lista de tarefas no sistema operacional

    def get_config_atual(self) -> dict:
        """Retorna a configuração atual do sistema operacional."""
        tarefas = [] # inicializa a lista de tarefas
        # transforma as tarefas em dicionários para a utilização nas modais
        for tarefa in self.filaTodasTarefas:
            tarefa_dict = {
                'id': tarefa.id,
                'cor': tarefa.cor,
                'ingresso': tarefa.ingresso,
                'duracao': tarefa.duracao,
                'prioridade': tarefa.prioridade,
                'eventos': [{'tipo_evento': evento.tipo, 'instante': evento.instante, 'duracao': evento.duracao} for evento in tarefa.eventos]
            }
            tarefas.append(tarefa_dict) # adiciona a tarefa à lista
        # retorna o dicionário com a configuração atual
        return {
            'tipo_escalonador': self.nome_tipo_escalonador,
            'quantum': self.quantum,
            'tarefas': tarefas
        }

    def setar_quantum(self, quantum: int) -> None:
        """Define o quantum para o sistema operacional."""
        self.quantum = quantum
    
    def setar_tarefas(self, tarefas: List[Tarefa]) -> None:
        """Define a lista de tarefas para o sistema operacional."""
        self.filaTodasTarefas = tarefas

    def criar_escalonador(self, tipo: str) -> None:
        """Cria o escalonador apropriado com base no tipo especificado."""
        self.nome_tipo_escalonador = tipo # armazena o nome do tipo de escalonador
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
        """Limpa todas as filas de tarefas e reseta o clock."""

        self.filaTodasTarefas.clear()
        self.filaTarefasProntas.clear()
        self.clock_sistema = 0
        self. mutexes = {}

    def executar_tarefas(self) -> None:
        """chama a função executar das tarefas na fila de tarefas."""
        for tarefa in self.filaTodasTarefas:
            if not tarefa.finalizada:
                tarefa.executar()

    # realiza o primeiro passo da simulação -- necessário para inicializar o sistema corretamente
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

        for tarefa in self.filaTodasTarefas: # percorre todas as tarefas
            if (tarefa.finalizada is False): # se a tarefa não estiver finalizada
                tarefa.atualizar_estado(self.clock_sistema) # atualiza o estado da tarefa

    def atualizarFilaProntas(self) -> None: # atualiza a fila de tarefas prontas
        """Atualiza a fila de tarefas prontas com base no estado das tarefas."""
        for tarefa in self.filaTodasTarefas: # percorre todas as tarefas
            if tarefa.pronta and (tarefa not in self.filaTarefasProntas): # se a tarefa estiver pronta e não estiver na fila de prontas
                self.adicionar_tarefa_pronta(tarefa) # adiciona a tarefa à fila de prontas
                self.ingresso_fila_prontas = True # indica que houve ingresso na fila de prontas
            
            elif not tarefa.pronta and (tarefa in self.filaTarefasProntas): # se a tarefa não estiver pronta e estiver na fila de prontas
                self.remover_tarefa_pronta(tarefa) # remove a tarefa da fila de prontas

    def analisar_tarefas(self) -> None:
        """Analisa as tarefas após a execução do sistema operacional."""
        # verifica se há alguma tarefa executando
        tarefa_executando = next((tarefa for tarefa in self.filaTodasTarefas if tarefa.executando), None)

        # verifica se há necessidade de escalonamento -- necessário quando há tarefas prontas e nenhuma executando, alguma tarefa ingressou na fila de prontas ou o quantum foi atingido
        if (len(self.filaTarefasProntas) > 0 and tarefa_executando is None) or self.ingresso_fila_prontas or (self.quantum > 0 and self.tempo_executando_atual >= self.quantum):
            for tarefa in self.filaTodasTarefas: # percorre todas as tarefas
                if tarefa.executando: # se a tarefa estiver executando, para de executar
                    tarefa.ficar_pronta() # coloca a tarefa como pronta
                    self.remover_tarefa_pronta(tarefa) # remove a tarefa da fila de prontas
                    self.adicionar_tarefa_pronta(tarefa) # adiciona a tarefa de volta à fila de prontas
                    break

            if self.ingresso_fila_prontas: # reseta o indicador de ingresso na fila de prontas
                self.ingresso_fila_prontas = False # reseta o indicador de ingresso na fila de prontas
                
            if len(self.filaTarefasProntas) > 0: # se houver tarefas prontas, chama o escalonador
                self.escalonador.escalonar() # chama o escalonador
            self.tempo_executando_atual = 0 # reseta o tempo de execução atual
