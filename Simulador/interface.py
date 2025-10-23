import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from SO import SO  # Importa a classe SO refatorada
from tarefa import Tarefa  # Importa Tarefa para type hints
import os
import matplotlib
matplotlib.use("TkAgg")  # Define o backend do matplotlib para o Tkinter
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# Lista de cores para o Gantt. O arquivo de config usa 'cor' como índice.
CORES_TAREFAS = [
    "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#00FFFF", "#FF00FF",
    "#800000", "#008000", "#000080", "#808000", "#008080", "#800080",
    "#C0C0C0", "#FF6347", "#ADFF2F", "#1E90FF", "#FFD700", "#40E0D0"
]


class Interface:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Escalonamento")
        self.root.geometry("1920x1080")

        self.so = SO(escalonador=None, filaTarefasProntas=[], filaTodasTarefas=[])
        self.config_filepath = "config.txt"  # Caminho padrão
        self.running = False
        
        # Atibutos do Gantt
        self.gantt_fig: Figure = None
        self.gantt_ax = None 
        self.gantt_canvas_widget = None 
        self.gantt_toolbar = None

        self.setup_interface()
        self.carrega_config(self.config_filepath)  # Tenta carregar config padrão

    def setup_interface(self):
        # Frame de Controles
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(fill='x', side='top')

        self.load_button = ttk.Button(control_frame, text="Carregar Config", command=self.seleciona_config)
        self.load_button.pack(side='left', padx=5)

        self.reset_button = ttk.Button(control_frame, text="Resetar Simulação", command=self.reseta_simulacao)
        self.reset_button.pack(side='left', padx=5)

        self.step_button = ttk.Button(control_frame, text="Executar Passo", command=self.passo)
        self.step_button.pack(side='left', padx=5)

        self.run_button = ttk.Button(control_frame, text="Executar Completo", command=self.executar_completo)
        self.run_button.pack(side='left', padx=5)

        self.stop_button = ttk.Button(control_frame, text="Parar", command=self.parar)
        self.stop_button.pack(side='left', padx=5)

        self.clock_label = ttk.Label(control_frame, text="Clock: 0", font=("Arial", 14, "bold"))
        self.clock_label.pack(side='right', padx=10)

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
            self.config_filepath = filepath
            self.so = SO(escalonador=None, filaTarefasProntas=[], filaTodasTarefas=[])
            self.so.configurar_sistema(self.config_filepath)
            self.limpa_interface()
            self.atualiza_interface()

        except FileNotFoundError:
            messagebox.showwarning("Aviso", f"Arquivo '{filepath}' não encontrado. Carregue um arquivo de configuração.")
        except Exception as e:
            messagebox.showerror("Erro ao Carregar", f"Erro ao processar arquivo de configuração: {e}")

    def reseta_simulacao(self):
        if not self.config_filepath:
            messagebox.showerror("Erro", "Nenhum arquivo de configuração carregado.")
            return
        self.carrega_config(self.config_filepath)

    def limpa_interface(self):
        """Limpa a GUI para uma nova simulação"""
        self.running = False
        
        # Limpa os eixos
        self.gantt_ax.clear()

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
        self.gantt_ax.grid(True, axis='x', linestyle='--', alpha=0.6) # Adiciona grade vertical

        # 3. Ajusta o layout e redesenha
        self.gantt_fig.tight_layout()
        self.gantt_canvas_widget.draw()

    def passo(self):
        """Executa um único passo"""
        if self.running:
            self.parar()

        if not self.so.filaTodasTarefas:
            messagebox.showwarning("Aviso", "Nenhuma tarefa carregada. Carregue um arquivo de configuração.")
            return

        if not self.so.executar_passo():
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
        if self.running:
            if not self.so.executar_passo():
                self.termina_simulacao()
            else:
                self.atualiza_interface()
                # Atualiza a GUI a cada 100ms
                self.root.after(100, self.loop_executar)

    def termina_simulacao(self):
        self.running = False
        self.alternar_botoes(enabled=True)
        messagebox.showinfo("Simulação Concluída", "A simulação de todas as tarefas foi finalizada.")
        
        # Pergunta se o usuário quer salvar o gráfico
        if messagebox.askyesno("Salvar Gráfico", "Deseja salvar o gráfico de Gantt como PNG?"):
            self.salvar_gantt()

    def atualiza_interface(self):
        """Atualiza todos os elementos da GUI com base no estado do SO."""

        # Atualiza Clock
        self.clock_label.config(text=f"Clock: {self.so.clock_sistema}")

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

        # Atualiza Gráfico de Gantt
        t = self.so.clock_sistema
        if t == 0:  # Não há o que desenhar no clock 0
            return

        x_start = t - 1  # O tick atual começa no tempo t-1 e vai até t

        for i, tarefa in enumerate(self.so.filaTodasTarefas):
            if tarefa.executando:
                # Usa 'cor' do config como índice
                cor_hex = CORES_TAREFAS[tarefa.cor % len(CORES_TAREFAS)]
                
                # Desenha uma barra horizontal
                # y=i (posição da tarefa), width=1 (duração de 1 tick), left=x_start
                self.gantt_ax.barh(i, width=1, left=x_start, height=0.7, 
                                 color=cor_hex, edgecolor='black', alpha=0.8)

            elif tarefa.pronta:
                # Desenha um ponto para indicar "pronta" 
                self.gantt_ax.plot(x_start + 0.5, i, 'o', color='#AAAAAA', markersize=2)

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