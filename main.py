import sys
import os
import importlib.util
import tkinter as tk
from tkinter import messagebox

# =============================================================================
# TEMPLATE COM UM NOVO ESCALONADOR DE EXEMPLO ("TESTE")
# =============================================================================
CODIGO_PADRAO_ESCALONADORES = r'''
from dataclasses import dataclass
from typing import List
from abc import ABC
from abc import abstractmethod
try:
    # Tenta importar do jeito relativo (Funciona quando compilado internamente)
    from .tarefa import Tarefa
except (ImportError, ValueError):
    # Se der erro de "parent package", tenta importar direto (Funciona como Plugin externo)
    # Graças àquele 'sys.modules' que adicionamos no main, ele vai achar a tarefa interna!
    from tarefa import Tarefa
import random
lista_escalonadores = ["FCFS", "PRIOP", "SRTF", "PRIOPEnv"]
indice_escalonador = {
    "FCFS": 0,
    "PRIOP": 1,
    "SRTF": 2,
    "PRIOPEnv": 3 # manter nome como está aqui para compatibilidade com SO.py e colocar o indice correto
}
# Classe base para escalonadores
@dataclass
class Escalonador(ABC):
    tarefas: List[Tarefa]   # Lista de tarefas a serem escalonadas
    nome_escalonador: str # Nome do escalonador
    tarefa_atual: Tarefa = None  # Tarefa atualmente em execução
    escolha_aleatoria_em_empate: bool = False  # Define se a escolha em casos de empate é aleatória
    # método abstrato para escalonar -- chamada do mesmo método para todos os escalonadores
    @abstractmethod
    def escalonar(self) -> None:
        """Executa o escalonamento das tarefas."""
        raise NotImplementedError
    
    # criação de escalonador específicos abaixo
    @staticmethod
    def criar_escalonador(tipo: str, tarefas: List[Tarefa], fator_envelhecimento: int) -> 'Escalonador':
        """Fábrica para criar escalonadores específicos com base no tipo."""
        if tipo == "FCFS":
            return EscalonadorFCFS(tarefas = tarefas, nome_escalonador="FCFS")
        elif tipo == "PRIOP":
            return EscalonadorPRIOP(tarefas = tarefas, nome_escalonador="PRIOP")
        elif tipo == "SRTF":
            return EscalonadorSRTF(tarefas = tarefas, nome_escalonador="SRTF")
        elif tipo == "PRIOPEnv":
            if fator_envelhecimento is None or fator_envelhecimento <= 0:
                raise ValueError("Fator de envelhecimento deve ser fornecido para o escalonador PRIOPEnv e deve ser maior que zero.")
            return EscalonadorPRIOPEnv(tarefas = tarefas, fator_envelhecimento = fator_envelhecimento, nome_escalonador="PRIOPEnv")
        else:
            raise ValueError("Tipo de escalonador desconhecido.")

    def escolha_em_casos_empate(self, tarefas_empatadas) -> None:
        """Define a estratégia de escolha em casos de empate."""
        # (1) a tarefa selecionada é a que está executando imediatamente
        # antes do (para evitar uma troca de contexto para a própria tarefa);
        if self.tarefa_atual in tarefas_empatadas:
            self.tarefa_atual.resetar_prioridade_dinamica()  # Reseta a prioridade dinâmica após seleção
            self.tarefa_atual.iniciar_execucao()
            return
        # (2) o instante de ingresso da tarefa:
        # quem chegou antes é escolhida; 
        menor_ingresso = float('inf')
        for tarefa in tarefas_empatadas:
            if tarefa.ingresso < menor_ingresso:
                menor_ingresso = tarefa.ingresso
        tarefas_menor_ingresso = [tarefa for tarefa in tarefas_empatadas if tarefa.ingresso == menor_ingresso]
        if len(tarefas_menor_ingresso) == 1:
            self.tarefa_atual = tarefas_menor_ingresso[0]
            tarefas_menor_ingresso[0].resetar_prioridade_dinamica()  # Reseta a prioridade dinâmica após seleção
            tarefas_menor_ingresso[0].iniciar_execucao()  # Retorna a tarefa com menor ingresso
            return
        # (3) duração da tarefa: duração menor deve ser escolhida;
        menor_duracao = float('inf')
        for tarefa in tarefas_menor_ingresso:
            if tarefa.duracao < menor_duracao:
                menor_duracao = tarefa.duracao
        tarefas_menor_duracao = [tarefa for tarefa in tarefas_menor_ingresso if tarefa.duracao == menor_duracao]
        if len(tarefas_menor_duracao) == 1:
            self.tarefa_atual = tarefas_menor_duracao[0]
            tarefas_menor_duracao[0].resetar_prioridade_dinamica()  # Reseta a prioridade dinâmica após seleção
            tarefas_menor_duracao[0].iniciar_execucao()  # Retorna a tarefa com menor duração
            return
        # (4) sorteio (isso deve ser indicado de alguma forma no gráfico de gantt).
        self.tarefa_atual = random.choice(tarefas_menor_duracao)
        self.tarefa_atual.resetar_prioridade_dinamica()  # Reseta a prioridade dinâmica após seleção
        self.tarefa_atual.iniciar_execucao()  # Retorna a tarefa sorteada
        self.escolha_aleatoria_em_empate = True  # Indica que a escolha foi aleatória

@dataclass
class EscalonadorFCFS(Escalonador):

    def escalonar(self) -> None:
        """Executa o escalonamento das tarefas usando o algoritmo FCFS."""
        if self.tarefas is None or len(self.tarefas) == 0:
            return
        
        # tarefas já ordenadas pq é uma fila
        self.tarefa_atual = self.tarefas[0]
        self.tarefas[0].iniciar_execucao()  # Retorna a primeira tarefa da fila


# implementação do escalonador de Prioridade Preemptiva
@dataclass
class EscalonadorPRIOP(Escalonador):

    def escalonar(self) -> None:
        """Executa o escalonamento das tarefas usando o algoritmo de Prioridade Preemptiva."""
        self.escolha_aleatoria_em_empate = False  # Reseta a flag de escolha aleatória em empate
        if self.tarefas is None or len(self.tarefas) == 0:
            return
        maior_prioridade = -1
        for tarefa in self.tarefas:
            if tarefa.prioridade_estatica > maior_prioridade:
                maior_prioridade = tarefa.prioridade_estatica
        # verifica se há mais de uma tarefa com a maior prioridade
        tarefas_maior_prio = [tarefa for tarefa in self.tarefas if tarefa.prioridade_estatica == maior_prioridade]
        if len(tarefas_maior_prio) == 1:
            self.tarefa_atual = tarefas_maior_prio[0]
            tarefas_maior_prio[0].iniciar_execucao()  # Retorna a tarefa com maior prioridade
            return
        self.escolha_em_casos_empate(tarefas_maior_prio)  # Chama o método de escolha em casos de empate
        

# implementação do escalonador SRTF
@dataclass
class EscalonadorSRTF(Escalonador):
    def escalonar(self) -> None:
        """Executa o escalonamento das tarefas usando o algoritmo SRTF."""
        self.escolha_aleatoria_em_empate = False  # Reseta a flag de escolha aleatória em empate
        if self.tarefas is None or len(self.tarefas) == 0:
            return

        menor_tempo_restante = float('inf')
        for tarefa in self.tarefas:
            if tarefa.t_restante < menor_tempo_restante:
                menor_tempo_restante = tarefa.t_restante
        # verifica se há mais de uma tarefa com o menor tempo restante
        tarefas_menor_tempo = [tarefa for tarefa in self.tarefas if tarefa.t_restante == menor_tempo_restante]
        if len(tarefas_menor_tempo) == 1:
            self.tarefa_atual = tarefas_menor_tempo[0]
            tarefas_menor_tempo[0].iniciar_execucao()  # Retorna a tarefa com menor tempo restante
            return
        self.escolha_em_casos_empate(tarefas_menor_tempo)  # Chama o método de escolha em casos de empate

# implementação do escalonador de Prioridade Preemptiva com Envelhecimento
@dataclass
class EscalonadorPRIOPEnv(Escalonador):
    fator_envelhecimento: int = 0  # Fator de envelhecimento para aumentar a prioridade das tarefas

    def escalonar(self) -> None:
        """Executa o escalonamento das tarefas usando o algoritmo de Prioridade Preemptiva com Envelhecimento."""
        self.escolha_aleatoria_em_empate = False  # Reseta a flag de escolha aleatória em empate
        if self.tarefas is None or len(self.tarefas) == 0:
            return

        # Aplica envelhecimento às tarefas
        for tarefa in self.tarefas:
            tarefa.prioridade_dinamica += self.fator_envelhecimento
        maior_prioridade = -1
        
        # vêifica a maior prioridade dinâmica
        for tarefa in self.tarefas:
            if tarefa.prioridade_dinamica > maior_prioridade:
                maior_prioridade = tarefa.prioridade_dinamica

        # verifica se há mais de uma tarefa com a maior prioridade
        tarefas_maior_prio = [tarefa for tarefa in self.tarefas if tarefa.prioridade_dinamica == maior_prioridade]
        if len(tarefas_maior_prio) == 1:
            self.tarefa_atual = tarefas_maior_prio[0]
            tarefas_maior_prio[0].resetar_prioridade_dinamica()  # Reseta a prioridade dinâmica após seleção
            tarefas_maior_prio[0].iniciar_execucao()  # Retorna a tarefa com maior prioridade
            return
        self.casos_empate_priopenv(tarefas_maior_prio)  # Chama o método de escolha em casos de empate

    def casos_empate_priopenv(self, tarefas_empatadas) -> None:
        """Define a estratégia de escolha em casos de empate."""
        # primeiro tenta desempate por prioridade estática
        maior_prioridade_estatica = -1
        for tarefa in tarefas_empatadas:
            if tarefa.prioridade_estatica > maior_prioridade_estatica:
                maior_prioridade_estatica = tarefa.prioridade_estatica
        tarefas_maior_prio_estatica = [tarefa for tarefa in tarefas_empatadas if tarefa.prioridade_estatica == maior_prioridade_estatica]
        if len(tarefas_maior_prio_estatica) == 1:
            self.tarefa_atual = tarefas_maior_prio_estatica[0]
            tarefas_maior_prio_estatica[0].resetar_prioridade_dinamica()  # Reseta a prioridade dinâmica após seleção
            tarefas_maior_prio_estatica[0].iniciar_execucao()  # Retorna a tarefa com maior prioridade estática
            return

        self.escolha_em_casos_empate(tarefas_maior_prio_estatica)  # Chama o método de escolha em casos de empate

'''
# =============================================================================
# LÓGICA DE INJEÇÃO TOTAL (CLASSES + DADOS)
# =============================================================================
def injetar_plugin_completo():
    if getattr(sys, 'frozen', False):
        pasta_app = os.path.dirname(sys.executable)
    else:
        pasta_app = os.path.dirname(os.path.abspath(__file__))
    arquivo_externo = os.path.join(pasta_app, "escalonadores.py")

    # Criação do arquivo
    if not os.path.exists(arquivo_externo):
        root = tk.Tk(); root.withdraw()
        if messagebox.askyesno("Configuração", "Criar arquivo 'escalonadores.py' externo?"):
            try:
                with open(arquivo_externo, "w", encoding="utf-8") as f:
                    f.write(CODIGO_PADRAO_ESCALONADORES)
                messagebox.showinfo("Sucesso", "Arquivo criado. Reiniciando.")
            except Exception as e:
                messagebox.showerror("Erro", str(e))
        root.destroy()

    # Importa o interno para ter a base
    try:
        import Simulador.escalonadores as interno
        print("-> [SISTEMA] Base interna carregada.")
    except ImportError:
        return

    # Se tiver plugin, injetar
    if os.path.exists(arquivo_externo):
        try:
            print(f"-> [PLUGIN] Carregando: {arquivo_externo}")
            
            spec = importlib.util.spec_from_file_location("Simulador.escalonadores", arquivo_externo)
            mod_externo = importlib.util.module_from_spec(spec)
            mod_externo.__package__ = "Simulador" 
            spec.loader.exec_module(mod_externo)
            
            # 1. Atualiza listas (Para a Interface ver os nomes novos)
            interno.lista_escalonadores[:] = mod_externo.lista_escalonadores
            interno.indice_escalonador.clear()
            interno.indice_escalonador.update(mod_externo.indice_escalonador)
            
            # Varremos o arquivo externo procurando tudo que for classe de Escalonador
            # e jogamos dentro do módulo interno.
            
            # Primeiro, substituímos a classe BASE (onde fica a fábrica criar_escalonador)
            interno.Escalonador = mod_externo.Escalonador

            for nome_atributo in dir(mod_externo):
                if nome_atributo.startswith("Escalonador"):
                    classe_nova = getattr(mod_externo, nome_atributo)
                    # Injeta a classe nova dentro do módulo interno
                    setattr(interno, nome_atributo, classe_nova)
                    print(f"   -> Classe injetada: {nome_atributo}")

        except Exception as e:
            root = tk.Tk(); root.withdraw()
            messagebox.showerror("Erro Plugin", f"Erro no arquivo externo:\n{e}")
            root.destroy()
    else:
        print("-> [PADRÃO] Usando interno.")

if __name__ == "__main__":
    
    injetar_plugin_completo()

    from Simulador import Interface 
    
    root = tk.Tk()
    app = Interface(root)
    root.mainloop()