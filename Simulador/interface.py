import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext  
import os
import matplotlib
matplotlib.use("TkAgg")  
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import copy
from typing import List
from .SO import SO
from .modalConfigManual import ModalConfigManual
from .modalAjuda import ModalAjuda
from .cores import COR_TAREFA_NAO_EXECUTANDO
class Interface:
    """Classe principal da interface do simulador."""
    def __init__(self, root):
        self.root = root # janela principal
        self.root.title("Simulador de Escalonamento") # título da janela
        self.root.geometry("1920x1080") # tamanho da janela
        self.so = SO(escalonador=None, filaTarefasProntas=[], filaTodasTarefas=[]) # sistema operacional simulado
        self.config_filepath = "config.txt"  # Caminho padrão
        self.running = False # Flag para execução contínua
        self.primeiro_passo_executado = False # Flag para o primeiro passo
        self.historico_estados: List[SO] = []  # Histórico de estados do SO
        self.historico_desenhos_gantt = []

        # Atributos do Gantt
        self.gantt_fig: Figure = None
        self.gantt_ax = None
        self.gantt_canvas_widget = None
        self.gantt_toolbar = None
        self.configs_atuais = None
        self.setup_interface() # configura a interface gráfica

    def setup_interface(self):
        """Configura todos os elementos da interface gráfica."""
        # Frame de Controles
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(fill='x', side='top')

        # Menu de Configuração
        self.load_button = ttk.Menubutton(control_frame, text="Configurar Sistema ▾")
        self.load_button.pack(side='left', padx=5)

        self.config_menu = tk.Menu(self.load_button, tearoff=0) # menu suspenso

        self.load_button["menu"] = self.config_menu # associa o menu ao botão

        self.config_menu.add_command(
            label="Carregar de Arquivo",
            command=self.seleciona_config
        ) # comando para carregar de arquivo

        self.config_menu.add_command(
            label="Configurar Manualmente",
            command=self.abrir_modal_config_manual
        ) # comando para configuração manual

        self.config_menu.add_separator() # separador no menu
        self.config_menu.add_command(
            label="Guia do Formato de Arquivo...",
            command=self.abrir_modal_ajuda
        ) # comando para abrir a modal de ajuda

        self.reset_button = ttk.Button(control_frame, text="Resetar Simulação", command=self.reseta_simulacao)
        self.reset_button.pack(side='left', padx=5) # botão de resetar simulação

        self.back_button = ttk.Button(control_frame, text="Retroceder", command=self.retroceder)
        self.back_button.pack(side='left', padx=5)

        self.step_button = ttk.Button(control_frame, text="Executar Passo", command=self.passo)
        self.step_button.pack(side='left', padx=5) # botão de executar passo

        self.run_button = ttk.Button(control_frame, text="Executar Completo", command=self.executar_completo)
        self.run_button.pack(side='left', padx=5) # botão de executar completo

        self.stop_button = ttk.Button(control_frame, text="Parar", command=self.parar)
        self.stop_button.pack(side='left', padx=5) # botão de parar

        self.clock_label = ttk.Label(control_frame, text="Clock: 0", font=("Arial", 14, "bold"))
        self.clock_label.pack(side='right', padx=10) # label do clock do sistema

        self.scheduler_info_label = ttk.Label(control_frame, text="Escalonador: --", font=("Arial", 11))
        self.scheduler_info_label.pack(side='right', padx=15)

        # Frame Principal
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill='both', expand=True)

        # Frame de Status das Tarefas
        status_frame = ttk.LabelFrame(main_frame, text="Estado das Tarefas", padding=10)
        status_frame.pack(fill='x', side='bottom', pady=10)

        self.task_status_text = scrolledtext.ScrolledText(status_frame, height=10, width=100, wrap=tk.WORD)
        self.task_status_text.pack(fill='both', expand=True)
        self.task_status_text.config(state='disabled')  # Torna somente leitura

        # Frame do Gráfico de Gantt
        gantt_frame = ttk.LabelFrame(main_frame, text="Gráfico de Gantt", padding=10)
        gantt_frame.pack(fill='both', expand=True)

        # Cria a Figura e os Eixos do Matplotlib
        self.gantt_fig = Figure(figsize=(5, 4), dpi=100)
        self.gantt_ax = self.gantt_fig.add_subplot(111)

        # Cria o widget Canvas do Tkinter para o Matplotlib
        self.gantt_canvas_widget = FigureCanvasTkAgg(self.gantt_fig, master=gantt_frame)
        self.gantt_canvas_widget.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Adiciona a barra de ferramentas
        self.gantt_toolbar = NavigationToolbar2Tk(self.gantt_canvas_widget, gantt_frame)
        self.gantt_toolbar.update()
        self.gantt_canvas_widget.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def abrir_modal_config_manual(self):
        """Cria e exibe a modal Nível 1."""
        # 'self.root' é a janela principal (tk.Tk)

        if self.configs_atuais:
            configuracao_existente = self.configs_atuais
        elif self.so.filaTodasTarefas:
            configuracao_existente = self.so.get_config_atual()
        else:
            configuracao_existente = None

        modal_nivel_1 = ModalConfigManual(self.root, configuracao_existente=configuracao_existente) 
        # processamento dos dados da modal

        if modal_nivel_1.resultado:
            self.configurar_sistema(modal_nivel_1.resultado['tipo_escalonador'], modal_nivel_1.resultado['quantum'], modal_nivel_1.resultado['fator_envelhecimento'], modal_nivel_1.resultado['tarefas'])

        else:
            messagebox.showinfo("Configuração Manual não concluída", "A configuração manual foi cancelada.")

    def abrir_modal_ajuda(self):
        """Abre a modal de ajuda sobre o formato do arquivo de configuração."""
        ModalAjuda(self.root)

    def configurar_sistema(self, tipo_escalonador, quantum, fator_envelhecimento, tarefas) -> None:
        try:
            self.primeiro_passo_executado = False
            self.running = False
            self.so = SO(escalonador=None, filaTarefasProntas=[], filaTodasTarefas=[])
            self.so.configurar_sistema_manual(tipo_escalonador, quantum, fator_envelhecimento, tarefas)
            self.historico_estados.clear() # Limpa o histórico
            self.limpa_interface()
            self.so.primeiro_passo()
            self.inicializa_interface()
        
        except Exception as e:
            messagebox.showerror("Erro na Configuração Manual", f"Erro ao configurar o sistema manualmente: {e}")

    def seleciona_config(self):
        filepath = filedialog.askopenfilename(
            title="Selecionar arquivo de configuração",
            filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os arquivos", "*.*")],
            initialdir=os.getcwd()  # Começa no diretório atual
        )
        if filepath:
            self.carrega_config(filepath)

    def carrega_config(self, filepath):
        try:
            self.primeiro_passo_executado = False
            self.config_filepath = filepath
            self.so = SO(escalonador=None, filaTarefasProntas=[], filaTodasTarefas=[])
            self.so.configurar_sistema(self.config_filepath)
            self.limpa_interface()
            self.so.primeiro_passo()
            self.inicializa_interface()

        except FileNotFoundError:
            messagebox.showwarning("Aviso", f"Arquivo '{filepath}' não encontrado. Carregue um arquivo de configuração.")
        except Exception as e:
            messagebox.showerror("Erro ao Carregar", f"Erro ao processar arquivo de configuração: {e}")

    def reseta_simulacao(self):
        try:
            if self.configs_atuais:
                configs_atuais = self.configs_atuais
            else:
                configs_atuais = self.so.get_config_atual()
            self.historico_estados.clear()
            self.so = SO(escalonador=None, filaTarefasProntas=[], filaTodasTarefas=[])
            self.so.configurar_sistema_manual(configs_atuais['tipo_escalonador'], configs_atuais['quantum'], configs_atuais['fator_envelhecimento'], configs_atuais['tarefas'])
            self.primeiro_passo_executado = False
            self.running = False
            self.limpa_interface()
            self.so.primeiro_passo()
            self.inicializa_interface()
        except Exception as e:
            messagebox.showerror("Erro ao Resetar", f"Erro ao resetar a simulação: {e}")

    def limpa_interface(self):
        """Limpa a GUI para uma nova simulação"""
        self.running = False
        
        # Limpa os eixos
        self.gantt_ax.clear()
        self.historico_desenhos_gantt.clear()
        # Configura os eixos para o Gantt
        tarefas = self.so.filaTodasTarefas
        num_tarefas = len(tarefas)
        
        if num_tarefas > 0:
            self.gantt_ax.set_ylim(-0.5, num_tarefas - 0.5)
            # Define os ticks do eixo Y para corresponderem a cada tarefa
            self.gantt_ax.set_yticks(range(num_tarefas))
            # Define os rótulos do eixo Y para os IDs das tarefas
            self.gantt_ax.set_yticklabels([t.id for t in tarefas])
            # Inverte o eixo Y para T1 ficar no topo
            self.gantt_ax.invert_yaxis()
        
        self.gantt_ax.set_xlabel("Tempo (clock)")
        self.gantt_ax.set_ylabel("Tarefas")
        self.gantt_ax.grid(True, axis='x', linestyle='--', alpha=0.6)  # Adiciona grade vertical
        
        # Ajusta o layout e redesenha
        self.gantt_fig.tight_layout()
        self.gantt_canvas_widget.draw()

    def retroceder(self):
        """Volta um passo na simulação."""
        
        if not self.historico_estados:
            messagebox.showinfo("Aviso", "Não há estados anteriores para retroceder.")
            return

        # Recupera o último estado salvo (pop remove o último item da lista)
        estado_anterior = self.historico_estados.pop()

        # Substitui o SO atual pelo antigo
        self.so = estado_anterior

        # Ajusta flags se necessário
        # Se voltamos para o tempo 0, o primeiro passo não foi executado
        if self.so.clock_sistema == 0:
            self.primeiro_passo_executado = False
        
        self.running = False # Geralmente queremos pausar ao voltar
        self.alternar_botoes(enabled=True)

        # Atualiza a tela inteira com os dados do "passado"
        self.inicializa_interface()
        if self.historico_desenhos_gantt:
            # Pega a lista de desenhos feitos no último passo
            ultimos_desenhos = self.historico_desenhos_gantt.pop()
            
            # Remove cada desenho do gráfico
            for artista in ultimos_desenhos:
                artista.remove()

        # Ajusta o eixo X para voltar ao tempo anterior
        t = self.so.clock_sistema
        self.gantt_ax.set_xlim(left=max(0, t - 50), right=t + 5)
        
        # Redesenha o canvas (agora sem as barras removidas)
        self.gantt_canvas_widget.draw()
        

    def salvar_estado_atual(self):
        """Helper para salvar o histórico."""
        snapshot = copy.deepcopy(self.so)
        self.historico_estados.append(snapshot)

    def passo(self):
        """Executa um único passo"""

        if self.running:
            self.parar()
            
        if not self.so.filaTodasTarefas:
            messagebox.showwarning("Aviso", "Nenhuma tarefa carregada. Carregue um arquivo de configuração.")
            return
        
        # guarda o estado anterior do sistema operacional
        self.salvar_estado_atual()

        if not self.primeiro_passo_executado:
            self.atualiza_interface()
            self.primeiro_passo_executado = True

        elif not self.so.executar_passo():
            self.termina_simulacao()
        else:
            self.atualiza_interface()

    def executar_completo(self):
        """Executa a simulação completa"""
        if self.running:
            return
        if not self.so.filaTodasTarefas:
            messagebox.showwarning("Aviso", "Nenhuma tarefa carregada. Carregue um arquivo de configuração.")
            return
            
        self.running = True
        self.alternar_botoes(enabled=False)
        self.loop_executar()

    def parar(self):
        self.running = False
        self.alternar_botoes(enabled=True)

    def loop_executar(self):
        """Loop principal para o modo Executar Completo."""
        if not self.primeiro_passo_executado:
            self.atualiza_interface()
            self.primeiro_passo_executado = True
            self.root.after(100, self.loop_executar)

        elif self.running:
            self.salvar_estado_atual()
            if not self.so.executar_passo():
                self.termina_simulacao()
            else:
                self.atualiza_interface()
                # Atualiza a GUI a cada 100ms
                self.root.after(100, self.loop_executar)

    def atualiza_status_tarefas(self):
                # Atualiza Status das Tarefas
        status_lines = []
        for tarefa in self.so.filaTodasTarefas:
            line = f"ID: {tarefa.id} | Estado: {tarefa.estado} | Restante: {tarefa.t_restante} | Executado: {tarefa.t_executado}"
            if tarefa.bloqueada:
                line += f" (Bloqueado por {tarefa.t_bloqueado}/{tarefa.evento_bloqueio_atual.duracao})"
            status_lines.append(line)
        self.task_status_text.config(state='normal')
        self.task_status_text.delete('1.0', tk.END)
        self.task_status_text.insert(tk.END, "\n".join(status_lines))
        self.task_status_text.config(state='disabled')

    def termina_simulacao(self):
        self.running = False
        self.primeiro_passo_executado = False
        self.atualiza_status_tarefas()
        self.alternar_botoes(enabled=True)
        messagebox.showinfo("Simulação Concluída", "A simulação de todas as tarefas foi finalizada.")
        self.configs_atuais = self.so.get_config_atual()
        # Pergunta se o usuário quer salvar o gráfico
        if messagebox.askyesno("Salvar Gráfico", "Deseja salvar o gráfico de Gantt como PNG?"):
            self.salvar_gantt()
            
        self.so.limpeza_sistema()

    def inicializa_interface(self):
        """Inicializa todos os elementos da GUI com base no estado do SO."""
        # Atualiza Clock
        self.clock_label.config(text=f"Clock: {self.so.clock_sistema}")
        nome = self.so.nome_tipo_escalonador if self.so.nome_tipo_escalonador else "Não Configurado"
        self.scheduler_info_label.config(text=f"Escalonador: {nome}")
        # Atualiza Status das Tarefas
        self.atualiza_status_tarefas()

    def atualiza_interface(self):
        """Atualiza todos os elementos da GUI com base no estado do SO."""
        # Atualiza Clock
        self.clock_label.config(text=f"Clock: {self.so.clock_sistema+1}")
        
        self.atualiza_status_tarefas()
        
        # Atualiza Gráfico de Gantt
        t = self.so.clock_sistema

        x_start = t # O tick atual começa no tempo t e vai até t+1

        desenhos_agora = []

        for i, tarefa in enumerate(self.so.filaTodasTarefas):

            if tarefa.executando:
                cor_hex = tarefa.cor
                # Desenha uma barra horizontal
                # y=i (posição da tarefa), width=1 (duração de 1 tick), left=x_start
                container = self.gantt_ax.barh(i, width=1, left=x_start, height=0.7,
                                 color=cor_hex, edgecolor='black', alpha=0.8)

                for retangulo in container:
                    desenhos_agora.append(retangulo)

            elif tarefa.aguardando or tarefa.finalizada:
                    retorno_desenho = self.gantt_ax.plot(x_start + 0.5, i, 'o', color='#AAAAAA', markersize=2)
                    desenhos_agora.extend(retorno_desenho)
            else:
                    container = self.gantt_ax.barh(i, width=1, left=x_start, height=0.7,
                                     color=COR_TAREFA_NAO_EXECUTANDO, edgecolor='black', alpha=0.3)
                    for retangulo in container:
                        desenhos_agora.append(retangulo)

        self.historico_desenhos_gantt.append(desenhos_agora)
        
        # Auto-scroll: Ajusta o limite do eixo X para "seguir" o tempo
        # Mostra os últimos 50 ticks de tempo, ou começa do 0
        self.gantt_ax.set_xlim(left=max(0, t - 50), right=t + 5)
        
        # Redesenha o canvas
        self.gantt_canvas_widget.draw_idle()

    def alternar_botoes(self, enabled: bool):
        """Ativa/desativa botões durante a execução completa."""
        state = 'normal' if enabled else 'disabled'
        self.load_button.config(state=state)
        self.reset_button.config(state=state)
        self.back_button.config(state=state)
        self.step_button.config(state=state)
        self.run_button.config(state=state)

    def salvar_gantt(self):
        """Salva o gráfico de Gantt em um arquivo PNG."""
        filepath = filedialog.asksaveasfilename(
            title="Salvar Gráfico de Gantt como PNG",
            filetypes=[("PNG Image", "*.png")],
            defaultextension=".png",
            initialfile="gantt_chart.png"
        )
        if not filepath:
            return  # Usuário cancelou
            
        try:
            # Antes de salvar, ajusta o limite do eixo X para mostrar TUDO
            self.gantt_ax.set_xlim(left=0, right=self.so.clock_sistema)
            # Salva a figura
            self.gantt_fig.savefig(filepath)
            messagebox.showinfo("Exportação Concluída", f"Gráfico salvo como '{filepath}'.")
            # Retorna o zoom para o modo seguir
            self.gantt_ax.set_xlim(left=max(0, self.so.clock_sistema - 50), right=self.so.clock_sistema + 5)
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Falha ao salvar arquivo PNG: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = Interface(root)
    root.mainloop()