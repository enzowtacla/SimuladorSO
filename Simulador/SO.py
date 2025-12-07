from dataclasses import dataclass
from typing import List, Union
import os

from .tarefa import Tarefa, Evento
from .escalonadores import *
from .cores import get_cor_hex, get_cor_by_hex
# a classe do sistema operacional
@dataclass
class SO:
    """Representa o sistema operacional que gerencia o escalonamento das tarefas."""
    escalonador: Escalonador # Escalonador usado pelo sistema operacional -- adicionar os tipos aqui quando criar mais
    filaTodasTarefas: List[Tarefa]  # Fila com todas as tarefas
    filaTarefasProntas: List[Tarefa]  # Fila com tarefas prontas para execução
    clock_sistema: int = 0  # Relógio do sistema
    quantum: int = 0  # Quantum para escalonadores que usam time-slicing
    ingresso_fila_prontas: bool = False  # Indica se tarefas ingressaram na fila de prontas recentemente
    tempo_executando_atual: int = 0  # Tempo que a tarefa atual está executando
    nome_tipo_escalonador: str = "" # guarda o nome do tipo de escalonador usado atualmente
    tarefa_executando_anterior: Tarefa = None  # guarda a tarefa que estava executando no passo anterior
    fator_envelhecimento: int = 0  # fator de envelhecimento para escalonadores que o utilizam
    list_controladores_io: 'IOControllerList' = None  # Lista de controladores de I/O
    list_mutexes: 'MutexList' = None  # Lista de mutexes
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
            campos = linhas[0].strip().split(";")
            tipo_escalonador = campos[0]
            quantum = campos[1]
            if tipo_escalonador == lista_escalonadores[indice_escalonador["PRIOPEnv"]]:  # PRIOP com envelhecimento
                self.fator_envelhecimento = int(campos[2])  # define um fator de envelhecimento
            self.criar_escalonador(tipo_escalonador)
            self.quantum = int(quantum)

            #próximas linhas são as tarefas, então lê cada linha e cria as tarefas com base no modelo
            for linha in linhas[1:]:
                campos = linha.strip().split(";") # separa os campos da linha
                id = campos[0]
                cor = campos[1]
                if not cor.startswith("#"):
                    cor = f"#{cor}"  # adiciona o '#' se não estiver presente
                ingresso = int(campos[2])
                duracao = int(campos[3])
                prioridade_estatica = int(campos[4])
                
                # cria a tarefa com os dados lidos
                tarefa = Tarefa(
                    id=id,
                    cor=cor,
                    ingresso=int(ingresso),
                    duracao=int(duracao),
                    prioridade_estatica=int(prioridade_estatica),
                    prioridade_dinamica=int(prioridade_estatica),
                    eventos=[]
                )
                # lê os eventos, se houver
                for campo in campos[5:]:
                    if campo.strip(): 
                        tarefa.adicionar_evento(campo, self)

                # adiciona a tarefa à fila de todas as tarefas
                self.adicionar_tarefa(tarefa)

    def configurar_sistema_manual(self, tipo_escalonador: str, quantum: int, fator_envelhecimento: int, tarefas) -> None:
        """Configura o sistema operacional manualmente."""
        self.limpeza_sistema() # limpa o sistema antes de configurar
        self.fator_envelhecimento = fator_envelhecimento # define o fator de envelhecimento
        self.criar_escalonador(tipo_escalonador) # cria o escalonador
        self.setar_quantum(quantum) # define o quantum

        # transformar tarefas em realmente uma lista de tarefas e eventos em reais eventos
        tarefas_convertidas: List[Tarefa] = [] # inicializa a lista de tarefas convertidas
        for tarefa in tarefas:
            # cria o objeto Tarefa com os dados convertidos
            tarefa_convertida = Tarefa (
                id=tarefa['id'],
                cor=get_cor_hex(tarefa['cor']),
                ingresso=tarefa['ingresso'],
                duracao=tarefa['duracao'],
                prioridade_estatica=tarefa['prioridade_estatica'],
                prioridade_dinamica=tarefa['prioridade_estatica'],
                eventos=[])
            # percorre os eventos da tarefa e cria objetos Evento
            for evento in tarefa.get('eventos', []):
                tarefa_convertida.adicionar_evento(evento=evento, sistema=self) # adiciona o evento convertido à tarefa
            tarefas_convertidas.append(tarefa_convertida) # adiciona a tarefa convertida à lista
        self.setar_tarefas(tarefas_convertidas) # define a lista de tarefas no sistema operacional

    def get_config_atual(self) -> dict:
        """Retorna a configuração atual do sistema operacional."""
        tarefas = [] # inicializa a lista de tarefas
        # transforma as tarefas em dicionários para a utilização nas modais
        for tarefa in self.filaTodasTarefas:
            tarefa_dict = {
                'id': tarefa.id,
                'cor': (get_cor_by_hex(tarefa.cor) or 0),
                'ingresso': tarefa.ingresso,
                'duracao': tarefa.duracao,
                'prioridade_estatica': tarefa.prioridade_estatica,
                'eventos': [{'tipo_evento': evento.tipo, 'instante': evento.instante, 'duracao': evento.duracao if evento.tipo == "IO" else None, 'mutex_id': evento.mutex_id if evento.tipo in ["ML", "MU"] else None} for evento in tarefa.eventos]
            }
            tarefas.append(tarefa_dict) # adiciona a tarefa à lista
        # retorna o dicionário com a configuração atual
        return {
            'tipo_escalonador': self.nome_tipo_escalonador,
            'quantum': self.quantum,
            'fator_envelhecimento': self.fator_envelhecimento,
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
        self.escalonador = Escalonador.criar_escalonador(tipo, self.filaTarefasProntas, self.fator_envelhecimento) # cria o escalonador usando a fábrica

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
        self.tarefa_executando_anterior = None
        self.clock_sistema = 0

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
        self.tarefa_executando_anterior = next((tarefa for tarefa in self.filaTodasTarefas if tarefa.executando), None)
        self.escalonador.tarefa_atual = self.tarefa_executando_anterior  # atualiza a tarefa atual no escalonador
        # verifica se há necessidade de escalonamento -- necessário quando há tarefas prontas e nenhuma executando, alguma tarefa ingressou na fila de prontas ou o quantum foi atingido
        if (len(self.filaTarefasProntas) > 0 and self.tarefa_executando_anterior is None) or self.ingresso_fila_prontas or (self.quantum > 0 and self.tempo_executando_atual >= self.quantum):
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

    def tratar_req_inicio_io(self, evento_io, tarefa) -> None:
        """Trata a requisição de início de I/O."""
        pass  # Implementar a lógica de início de I/O aqui

    def tratar_req_fim_io(self, evento_io, tarefa) -> None:
        """Trata a requisição de fim de I/O."""
        pass  # Implementar a lógica de fim de I/O aqui

    def tratar_req_lock_mutex(self, evento_mutex, tarefa) -> None:
        """Trata a requisição de lock de mutex."""
        pass  # Implementar a lógica de lock de mutex aqui

    def tratar_req_unlock_mutex(self, evento_mutex, tarefa) -> None:
        """Trata a requisição de unlock de mutex."""
        pass  # Implementar a lógica de unlock de mutex aqui

class IOController:
    """Controlador de dispositivos de I/O."""
    id: str  # Identificador do controlador de I/O
    duracao_acesso: int  # Duração do acesso ao dispositivo de I/O
    tarefa: Tarefa  # Tarefa associada ao controlador de I/O
    SO: SO  # Referência ao sistema operacional
    def executar_io(self) -> None:
        """Executa a operação de I/O."""
        self.duracao_acesso -= 1  # Implementar a lógica de execução de I/O aqui
        if self.duracao_acesso < 0:
            self.IRQ()

    def IRQ(self) -> None:
        """Trata a requisição de I/O."""
        self.SO.tratar_req_fim_io(self, self.tarefa)

class IOControllerList:
    """Controlador de lista de dispositivos de I/O."""
    def __init__(self):
        self.controladores_io = []

    def adicionar_controlador_io(self, controlador_io: 'IOController', tarefa: 'Tarefa') -> None:
        """Adiciona um controlador de I/O à lista."""
        self.controladores_io.append(controlador_io)
        controlador_io.tarefa = tarefa

    def remover_controlador_io(self, id_controlador: str) -> None:
        """Remove um controlador de I/O da lista pelo seu ID."""
        self.controladores_io = [ctrl for ctrl in self.controladores_io if ctrl.id != id_controlador]

    def obter_controlador_io(self, id_controlador: str) -> Union['IOController', None]:
        """Obtém um controlador de I/O pelo seu ID."""
        for ctrl in self.controladores_io:
            if ctrl.id == id_controlador:
                return ctrl
        return None

class Mutex:
    """Representa um mutex para sincronização de tarefas."""
    id: str  # Identificador do mutex
    count: int = 1  # Contador de locks adquiridos
    tarefas_bloqueadas: List[Tarefa] = None  # Lista de tarefas bloqueadas pelo mutex
    def __post_init__(self):
        self.tarefas_bloqueadas = []  # Inicializa a lista de tarefas bloqueadas
    def lock(self, tarefa: Tarefa) -> None:
        """Adquire o lock do mutex para a tarefa."""
        if self.count > 0:
            self.count -= 1
        else:
            self.tarefas_bloqueadas.append(tarefa)
            tarefa.bloquear()
    def unlock(self) -> Union[Tarefa, None]:
        """Libera o lock do mutex e retorna a próxima tarefa bloqueada, se houver."""
        if self.tarefas_bloqueadas:
            tarefa_desbloqueada = self.tarefas_bloqueadas.pop(0)
            return tarefa_desbloqueada
        else:
            self.count += 1
            return None
class MutexList:
    """Controlador de lista de mutexes."""
    def __init__(self):
        self.mutexes = []

    def adicionar_mutex(self, mutex: 'Mutex') -> None:
        """Adiciona um mutex à lista."""
        self.mutexes.append(mutex)

    def remover_mutex(self, id_mutex: str) -> None:
        """Remove um mutex da lista pelo seu ID."""
        self.mutexes = [m for m in self.mutexes if m.id != id_mutex]

    def obter_mutex(self, id_mutex: str) -> Union['Mutex', None]:
        """Obtém um mutex pelo seu ID."""
        for m in self.mutexes:
            if m.id == id_mutex:
                return m
        return None


    def tratar_req_inicio_io(self, evento_io) -> None:
        """Trata a requisição de início de I/O."""
        tarefa = self.tarefa_executando_anterior
        if tarefa:
            tarefa.bloquear()  # Bloqueia a tarefa
            tarefa.evento_bloqueio_atual = evento_io
            self.tarefa_executando_anterior = None

    def tratar_req_fim_io(self, evento_io) -> None:
        """Trata a requisição de fim de I/O."""
        tarefa_desbloqueada = None
        for tarefa in self.filaTodasTarefas:
            if tarefa.bloqueada and tarefa.evento_bloqueio_atual == evento_io:
                tarefa_desbloqueada = tarefa
                break

        if tarefa_desbloqueada:
            tarefa_desbloqueada.ficar_pronta()  # Coloca a tarefa como pronta
            tarefa_desbloqueada.evento_bloqueio_atual = None
            self.adicionar_tarefa_pronta(tarefa_desbloqueada)  # Adiciona a tarefa à fila de prontas
            self.ingresso_fila_prontas = True  # Indica que houve ingresso na fila de prontas

    def tratar_req_lock_mutex(self, evento_mutex) -> None:
        """Trata a requisição de lock de mutex."""

        # Apenas bloqueia a tarefa
        tarefa = self.tarefa_executando_anterior
        if tarefa:
            tarefa.bloquear()
            tarefa.evento_bloqueio_atual = evento_mutex
            self.tarefa_executando_anterior = None

    def tratar_req_unlock_mutex(self, evento_mutex) -> None:
        """Trata a requisição de unlock de mutex."""

        # Encontra e desbloqueia a tarefa
        for tarefa in self.filaTodasTarefas:
            if tarefa.bloqueada and tarefa.evento_bloqueio_atual == evento_mutex:
                tarefa.ficar_pronta()
                tarefa.evento_bloqueio_atual = None
                self.adicionar_tarefa_pronta(tarefa)
                self.ingresso_fila_prontas = True
                break