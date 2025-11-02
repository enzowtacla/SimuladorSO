import tkinter as tk
from tkinter import ttk, messagebox

class ModalConfigManual(tk.Toplevel):
    
    def __init__(self, parent):
        # Chamar o construtor do Toplevel
        super().__init__(parent)
        
        self.title("Configuração Manual")
        self.resultado = None  # Para armazenar o resultado da configuração
        self.tipo_escalonador = None
        self.quantum = None
        self.tarefas = []

        # Criar a interface interna
        self._criar_widgets()
        # Configurar o comportamento modal
        self.transient(parent)
        self.grab_set()

        # Faz a Janela Principal esperar por esta
        parent.wait_window(self)

    def _criar_widgets(self):
        frame = ttk.Frame(self, padding="10")
        frame.pack(expand=True, fill='both')
        
        # seleção do tipo de escalonador
        ttk.Label(frame, text="Tipo de Escalonador:").pack(pady=5)
        self.tipo_escalonador = tk.StringVar()
        escalonador_menu = ttk.Combobox(
            frame, 
            textvariable=self.tipo_escalonador,
            values=["FCFS", "PRIOP", "SRTF"]
        )
        escalonador_menu.pack(pady=5, padx=10, fill="x")

        ttk.Label(frame, text="Quantum:").pack(pady=5)
        self.quantum = tk.IntVar(value=4)
        ttk.Entry(frame, textvariable=self.quantum).pack(pady=5, padx=10, fill="x")

        # --- Botão para chamar a Modal para Eventos das Tarefas ---
        ttk.Button(
            frame, 
            text="Adicionar Tarefa", 
            command=self._abrir_modal_tarefas
        ).pack(pady=(10, 0))

        # --- Mostrar as tarefas adicionadas ---
        self.lista_tarefas = tk.Listbox(frame)
        self.lista_tarefas.pack(expand=True, fill='both', pady=(5, 0))
        # --- Botões de Salvar/Cancelar ---
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=(20, 0))
        
        ttk.Button(btn_frame, text="Salvar", command=self._on_salvar).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self._on_cancelar).pack(side='left', padx=5)

    def _abrir_modal_tarefas(self):

        modal_tarefas = ModalTarefas(self)
        if modal_tarefas.resultado:
            tarefa = modal_tarefas.resultado
            # adicionar a tarefa à lista de tarefas
            if not hasattr(self, 'tarefas'):
                self.tarefas = []
            self.tarefas.append(tarefa)

    # Funções _on_salvar e _on_cancelar (permanecem iguais)
    def _on_salvar(self):
        self.resultado = {
            "tipo_escalonador": self.tipo_escalonador.get(),
            "quantum": self.quantum.get(),
            "tarefas": self.tarefas  # Supondo que 'self.tarefas' foi preenchida na modal avançada
        }
        self.destroy()

    def _on_cancelar(self):
        self.resultado = None
        self.destroy()

class ModalTarefas(tk.Toplevel):
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Configurações de Tarefas")
        
        self.resultado = None
        self.eventos = []

        self.criar_widgets()
        
        # --- Lógica Modal ---
        self.transient(parent)  
        self.grab_set()              
        parent.wait_window(self)  # Espera até fechar esta modal

    def criar_widgets(self):

        frame = ttk.Frame(self, padding="10")
        frame.pack(expand=True, fill='both')

        # Campos para definir atributos da tarefa
        ttk.Label(frame, text="ID da Tarefa:").pack(anchor='w', pady=(0, 5))
        self.id_tarefa_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.id_tarefa_var).pack(fill='x')

        ttk.Label(frame, text="Cor da Tarefa (Índice):").pack(anchor='w', pady=(10, 5))
        self.cor_tarefa_var = tk.IntVar()
        ttk.Entry(frame, textvariable=self.cor_tarefa_var).pack(fill='x')   

        ttk.Label(frame, text="Tempo de Ingresso:").pack(anchor='w', pady=(10, 5))
        self.ingresso_tarefa_var = tk.IntVar()
        ttk.Entry(frame, textvariable=self.ingresso_tarefa_var).pack(fill='x')

        ttk.Label(frame, text="Duração da Tarefa:").pack(anchor='w', pady=(10, 5))
        self.duracao_tarefa_var = tk.IntVar()
        ttk.Entry(frame, textvariable=self.duracao_tarefa_var).pack(fill='x')

        ttk.Label(frame, text="Prioridade da Tarefa:").pack(anchor='w', pady=(10, 5))
        self.prioridade_tarefa_var = tk.IntVar()
        ttk.Entry(frame, textvariable=self.prioridade_tarefa_var).pack(fill='x')

        # --- Botão para chamar a Modal para Eventos das Tarefas ---
        ttk.Button(
            frame, 
            text="Adicionar Evento", 
            command=self._abrir_modal_evento
        ).pack(pady=(10, 0))

        # --- Mostrar os eventos adicionados ---
        self.lista_eventos = tk.Listbox(frame)
        self.lista_eventos.pack(expand=True, fill='both', pady=(5, 0))

        # --- Botões de Salvar/Cancelar ---
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=(20, 0))
        
        ttk.Button(btn_frame, text="Salvar", command=self._on_salvar).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self._on_cancelar).pack(side='left', padx=5)

    def _abrir_modal_evento(self):
        modal_evento = ModalEvent(self)
        if modal_evento.resultado:
            evento = modal_evento.resultado
            # adicionar o evento à lista de eventos da tarefa
            if not hasattr(self, 'eventos'):
                self.eventos = []
            self.eventos.append(evento)

    def _on_salvar(self):
        # Coletar os dados da tarefa e fechar a modal
        self.resultado = {
            "id": self.id_tarefa_var.get(),
            "cor": self.cor_tarefa_var.get(),
            "ingresso": self.ingresso_tarefa_var.get(),
            "duracao": self.duracao_tarefa_var.get(),
            "prioridade": self.prioridade_tarefa_var.get(),
            "eventos": self.eventos  # Supondo que 'self.eventos' foi preenchida na modal de eventos
        }
        self.destroy()

    def _on_cancelar(self):
        self.resultado = None
        self.destroy()

class ModalEvent(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Adicionar Evento")

        # Definir Estado e Variáveis
        self.resultado = None
        self.nome_evento_var = tk.StringVar()

        # Chamar a criação da interface
        self._criar_widgets()

        # Configurar a lógica da modal
        self.transient(parent)
        self.grab_set()
        parent.wait_window(self)
        
    def _criar_widgets(self):
        """Toda a criação da interface vai aqui."""
        frame = ttk.Frame(self, padding="10")
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Nome do Evento:").pack(anchor='w', pady=(0, 5))
        
        entry_nome = ttk.Entry(frame, textvariable=self.nome_evento_var)
        entry_nome.pack(fill='x')
        
        # Foca no campo de entrada
        entry_nome.focus_set()

        # Botões
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(side='bottom', pady=(15, 0))
        
        ttk.Button(btn_frame, text="Salvar Evento", command=self._on_salvar).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self._on_cancelar).pack(side='left', padx=5)


    def _on_salvar(self):
        nome = self.nome_evento_var.get().strip()
        if not nome:
            messagebox.showerror("Erro", "Nome não pode ser vazio", parent=self)
            return

        self.resultado = {"nome_evento": nome}
        self.destroy() 
        
    def _on_cancelar(self):
        self.resultado = None
        self.destroy()