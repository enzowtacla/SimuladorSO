import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from SO import SO # Importa a classe SO refatorada
from tarefa import Tarefa # Importa Tarefa para type hints
import os

# Lista de cores para o Gantt[cite: 31]. O arquivo de config usa 'cor' como índice.
CORES_TAREFAS = [
    "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#00FFFF", "#FF00FF",
    "#800000", "#008000", "#000080", "#808000", "#008080", "#800080",
    "#C0C0C0", "#FF6347", "#ADFF2F", "#1E90FF", "#FFD700", "#40E0D0"
]

class Interface:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Escalonamento v0.1")
        self.root.geometry("1000x700")

        self.so = SO(escalonador=None, filaTarefasProntas=[], filaTodasTarefas=[])
        self.config_filepath = "config.txt"  # Caminho padrão
        self.running = False
        self.tick_scale = 10  # Largura de cada tickn o Gantt (em pixels)
        self.row_height = 30  # Altura de cada linha de tarefa no Gantt

        self.setup_gui()
        self.load_config(self.config_filepath) # Tenta carregar config padrão

    def setup_gui(self):
        # --- Frame de Controles ---
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(fill='x', side='top')

        self.load_button = ttk.Button(control_frame, text="Carregar Config", command=self.select_config_file)
        self.load_button.pack(side='left', padx=5)

        self.reset_button = ttk.Button(control_frame, text="Resetar Simulação", command=self.reset_simulation)
        self.reset_button.pack(side='left', padx=5)

        self.step_button = ttk.Button(control_frame, text="Executar Passo", command=self.step_gui)
        self.step_button.pack(side='left', padx=5)

        self.run_button = ttk.Button(control_frame, text="Executar Completo", command=self.run_gui)
        self.run_button.pack(side='left', padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="Parar", command=self.stop_gui)
        self.stop_button.pack(side='left', padx=5)

        self.clock_label = ttk.Label(control_frame, text="Clock: 0", font=("Arial", 14, "bold"))
        self.clock_label.pack(side='right', padx=10)

        # --- Frame Principal (Status e Gantt) ---
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill='both', expand=True)

        # --- Frame de Status das Tarefas ---
        status_frame = ttk.LabelFrame(main_frame, text="Estado das Tarefas", padding=10)
        status_frame.pack(fill='x', side='bottom', pady=10)
        
        # Usamos um ScrolledText para mostrar o estado, similar a um console/debugger
        self.task_status_text = scrolledtext.ScrolledText(status_frame, height=10, width=100, wrap=tk.WORD)
        self.task_status_text.pack(fill='both', expand=True)
        self.task_status_text.config(state='disabled') # Torna somente leitura

        # --- Frame do Gráfico de Gantt---
        gantt_frame = ttk.LabelFrame(main_frame, text="Gráfico de Gantt", padding=10)
        gantt_frame.pack(fill='both', expand=True)

        # Canvas com barras de rolagem
        self.gantt_canvas = tk.Canvas(gantt_frame, bg='white', scrollregion=(0, 0, 2000, 500))
        
        h_scroll = ttk.Scrollbar(gantt_frame, orient='horizontal', command=self.gantt_canvas.xview)
        v_scroll = ttk.Scrollbar(gantt_frame, orient='vertical', command=self.gantt_canvas.yview)
        
        self.gantt_canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)

        h_scroll.pack(side='bottom', fill='x')
        v_scroll.pack(side='right', fill='y')
        self.gantt_canvas.pack(side='left', fill='both', expand=True)

    def select_config_file(self):
        filepath = filedialog.askopenfilename(
            title="Selecionar arquivo de configuração",
            filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os arquivos", "*.*")],
            initialdir=os.getcwd() # Começa no diretório atual
        )
        if filepath:
            self.load_config(filepath)

    def load_config(self, filepath):
        try:
            self.config_filepath = filepath
            self.so = SO(escalonador=None, filaTarefasProntas=[], filaTodasTarefas=[])
            self.so.configurar_sistema(self.config_filepath)
            self.reset_simulation_view()
            self.update_gui()
            
        except FileNotFoundError:
            messagebox.showwarning("Aviso", f"Arquivo '{filepath}' não encontrado. Carregue um arquivo de configuração.")
        except Exception as e:
            messagebox.showerror("Erro ao Carregar", f"Erro ao processar arquivo de configuração: {e}")

    def reset_simulation(self):
        if not self.config_filepath:
            messagebox.showerror("Erro", "Nenhum arquivo de configuração carregado.")
            return
        self.load_config(self.config_filepath)

    def reset_simulation_view(self):
        """Limpa a GUI para uma nova simulação."""
        self.running = False
        self.gantt_canvas.delete("all")
        
        # Redesenha as linhas e nomes das tarefas
        num_tarefas = len(self.so.filaTodasTarefas)
        self.gantt_canvas.config(scrollregion=(0, 0, 2000, num_tarefas * self.row_height))

        for i, tarefa in enumerate(self.so.filaTodasTarefas):
            y = i * self.row_height
            # Linha da tarefa
            self.gantt_canvas.create_line(0, y + self.row_height, 2000, y + self.row_height, fill="#E0E0E0")
            # Nome da tarefa
            self.gantt_canvas.create_text(10, y + (self.row_height / 2), anchor='w', text=tarefa.id, font=("Arial", 10))
            
        # Linha de "base"
        self.gantt_canvas.create_line(50, 0, 50, num_tarefas * self.row_height, fill="black")


    def step_gui(self):
        """Executa um único passo"""
        if self.running:
            self.stop_gui()

        if not self.so.filaTodasTarefas:
            messagebox.showwarning("Aviso", "Nenhuma tarefa carregada. Carregue um arquivo de configuração.")
            return

        if not self.so.executar_passo():
            self.finish_simulation()
        else:
            self.update_gui()

    def run_gui(self):
        """Executa a simulação completa"""
        if self.running:
            return
            
        if not self.so.filaTodasTarefas:
            messagebox.showwarning("Aviso", "Nenhuma tarefa carregada. Carregue um arquivo de configuração.")
            return

        self.running = True
        self.toggle_controls(enabled=False)
        self.run_loop()

    def stop_gui(self):
        self.running = False
        self.toggle_controls(enabled=True)

    def run_loop(self):
        """Loop principal para o modo 'Executar Completo'."""
        if self.running:
            if not self.so.executar_passo():
                self.finish_simulation()
            else:
                self.update_gui()
                # Atualiza a GUI a cada 100ms
                self.root.after(100, self.run_loop)

    def finish_simulation(self):
        self.running = False
        self.toggle_controls(enabled=True)
        messagebox.showinfo("Simulação Concluída", "A simulação de todas as tarefas foi finalizada.")
        self.save_gantt() # Req 2.3

    def update_gui(self):
        """Atualiza todos os elementos da GUI com base no estado do SO."""
        
        # 1. Atualiza Clock
        self.clock_label.config(text=f"Clock: {self.so.clock_sistema}")

        # 2. Atualiza Status das Tarefas 
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

        # 3. Atualiza Gráfico de Gantt 
        t = self.so.clock_sistema
        x_start = 50 + ((t - 1) * self.tick_scale) # Começa 50px à direita
        x_end = 50 + (t * self.tick_scale)

        for i, tarefa in enumerate(self.so.filaTodasTarefas):
            y_start = i * self.row_height
            y_end = y_start + self.row_height

            if tarefa.executando:
                # Usa 'cor' do config como índice [cite: 31, 49]
                cor_hex = CORES_TAREFAS[tarefa.cor % len(CORES_TAREFAS)]
                self.gantt_canvas.create_rectangle(x_start, y_start, x_end, y_end, fill=cor_hex, outline=cor_hex, tags="gantt_bar")
            elif tarefa.pronta:
                 # indicador sutil para o modo de depuração (passo-a-passo)
                 self.gantt_canvas.create_rectangle(x_start + (self.tick_scale/2)-1, y_start + (self.row_height/2)-1, 
                                                   x_start + (self.tick_scale/2)+1, y_start + (self.row_height/2)+1, 
                                                   fill="#AAAAAA", outline="")
            
        # Auto-scroll
        if x_end > self.gantt_canvas.winfo_width():
             self.gantt_canvas.xview_moveto( (x_end - self.gantt_canvas.winfo_width() + 50) / self.gantt_canvas.cget("scrollregion").split(' ')[2] )

    def toggle_controls(self, enabled: bool):
        """Ativa/desativa botões durante a execução completa."""
        state = 'normal' if enabled else 'disabled'
        self.load_button.config(state=state)
        self.reset_button.config(state=state)
        self.step_button.config(state=state)
        self.run_button.config(state=state)

    def save_gantt(self):
        """Salva o gráfico de Gantt em um arquivo (Req 2.3)"""
        try:
            self.gantt_canvas.postscript(file="gantt_chart.ps", colormode='color',
                                         width=self.gantt_canvas.cget("scrollregion").split(' ')[2],
                                         height=self.gantt_canvas.cget("scrollregion").split(' ')[3])
            messagebox.showinfo("Exportação Concluída", 
                                "Gráfico de Gantt salvo como 'gantt_chart.ps'.\n"
                                "Este formato é exigido pela restrição de não usar bibliotecas externas.")
        except Exception as e:
            messagebox.showerror("Erro ao Exportar", f"Falha ao salvar arquivo PostScript: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = Interface(root)
    root.mainloop()