import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from .cores import get_lista_cores_para_combobox
from .eventos import lista_eventos_tipos
from .escalonadores import lista_escalonadores
# Modal de Ajuda sobre o formato do arquivo de configuração
class ModalAjuda(tk.Toplevel):
    """Classe para o modal de ajuda."""
    # Inicialização do modal
    def __init__(self, parent):
        """Inicializa o modal de ajuda."""
        super().__init__(parent) # inicializa a janela pai
        self.title("Guia de Formato de Arquivo de Configuração") # título do modal

        self.geometry("600x600") # tamanho do modal
        self.resizable(False, False) # desabilita redimensionamento

        self._criar_widgets() # cria os widgets do modal
        
        # Configuração modal
        self.transient(parent) # torna a janela modal em relação à janela pai
        self.grab_set() # captura todos os eventos para esta janela
        parent.wait_window(self) # espera até que a janela seja fechada

    def _criar_widgets(self):
        """Cria os widgets do modal."""
        frame = ttk.Frame(self, padding="10") # frame principal
        frame.pack(expand=True, fill='both') # expande para preencher a janela

        # Cria a área de texto rolável
        self.text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=30, width=80) # área de texto
        self.text_area.pack(expand=True, fill='both', pady=(0, 10)) # expande para preencher o frame

        # --- Define "tags" para formatação (ex: negrito) ---
        self.text_area.tag_configure("header", font=("Arial", 14, "bold"), spacing3=10) # configuração da tag de cabeçalho
        self.text_area.tag_configure("sub_header", font=("Arial", 12, "bold"), spacing3=5) # configuração da tag de subcabeçalho
        self.text_area.tag_configure("code", font=("Courier New", 10), background="#f0f0f0") # configuração da tag de código

        # --- Insere o Texto de Ajuda ---
        self._popular_texto_ajuda()

        # Torna o texto "somente leitura"
        self.text_area.config(state='disabled')

        # Botão para fechar
        btn_fechar = ttk.Button(frame, text="Fechar", command=self.destroy)
        btn_fechar.pack(side='bottom')

    def _popular_texto_ajuda(self):
        """Preenche a caixa de texto com o guia."""
        # --- Título ---
        self.text_area.insert(tk.END, "Guia do Formato de Arquivo\n", "header")
        self.text_area.insert(tk.END, 
            "O arquivo de configuração deve ser um .txt simples.\n\n"
        ) # inserção do título

        # --- 1. Linha do Sistema ---
        self.text_area.insert(tk.END, "Linha 1: Configuração do Sistema\n", "sub_header")
        self.text_area.insert(tk.END, "Formato: \n", "code")
        self.text_area.insert(tk.END, "algoritmo_escalonamento;quantum\n", "code")
        self.text_area.insert(tk.END, 
            "\nExemplo:\n", "code")
        self.text_area.insert(tk.END, "SRTF;4\n\n", "code")
        self.text_area.insert(tk.END, 
            "Algoritmos Válidos: \n", "code")
        for alg in lista_escalonadores:
            self.text_area.insert(tk.END, f"  {alg}\n", "code")
        self.text_area.insert(tk.END, "Quantum: Um número inteiro (ex: 4). Usado apenas por algoritmos preemptivos. Se for 0, o sistema não usa quantum\n\n"
        )
        self.text_area.insert(tk.END, 
            "Se o algoritmo escolhido o com envelhecimento (ex: PRIOPEnv), o fator de envelhecimento deve ser adicionado na primeira linha.\n\n"
        )
        # --- Exemplo de Linha com Fator de Envelhecimento ---
        self.text_area.insert(tk.END, "Exemplo com Fator de Envelhecimento:\n", "code")
        self.text_area.insert(tk.END, "PRIOPEnv;4;2\n\n", "code")
        self.text_area.insert(tk.END, 
            "Neste exemplo, o algoritmo é PRIOPEnv, quantum 4 e fator de envelhecimento 2.\n\n"
        )
        # --- 2. Linhas de Tarefa ---
        self.text_area.insert(tk.END, "Linhas 2..N: Definição de Tarefas\n", "sub_header")
        self.text_area.insert(tk.END, "Formato: \n", "code")
        self.text_area.insert(tk.END, "id;cor;ingresso;duracao;prioridade_estatica;lista_eventos\n\n", "code")
        
        self.text_area.insert(tk.END, 
            "id: Identificador (ex: t01).\n"
            "cor: no formato RGB em Hexadecimal.\n"
            "ingresso: Tick de relógio que a tarefa entra no sistema (ex: 0).\n"
            "duracao: Duração total de execução da tarefa (ex: 5).\n"
            "prioridade_estatica: Prioridade Estática (ex: 1). (Usado por PRIOP).\n"
            "lista_eventos: Lista de eventos (detalhes abaixo).\n\n"
        )

        # --- 3. Lista de Eventos ---
        self.text_area.insert(tk.END, "Formato da 'lista_eventos'\n", "sub_header")
        self.text_area.insert(tk.END, 
            "A lista é opcional. Se vazia, não inclua nada após a prioridade.\n"
            "Múltiplos eventos são separados por ;\n"
            "Cada evento tem formato específico:\n\n"
        )
        self.text_area.insert(tk.END, "Tipos de Eventos Válidos:\n", "code")
        self.text_area.insert(tk.END, "  IO: IO:ingresso-duracao\n", "code")
        self.text_area.insert(tk.END, "  Mutex Lock (id fica junto com tipo): MLid_mutex:ingresso\n", "code")
        self.text_area.insert(tk.END, "  Mutex Unlock (id fica junto com tipo): MUid_mutex:ingresso\n", "code")
        self.text_area.insert(tk.END, 
            "Exemplo de linha de tarefa COM eventos:\n", "code")
        self.text_area.insert(tk.END, "t01;F0E0D0;0;10;1;IO:2-3;ML1:6;MU1:8\n", "code")
        self.text_area.insert(tk.END, 
            "(Tarefa t01, cor F0E0D0, ingresso 0, duração 10, prio 1, com I/O no tempo 2, Lock no tempo 6, Unlock no tempo 8)\n\n"
        )
