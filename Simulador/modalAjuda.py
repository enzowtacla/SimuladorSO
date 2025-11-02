import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from .cores import get_lista_cores_para_combobox

class ModalAjuda(tk.Toplevel):
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Guia de Formato de Arquivo de Configuração")

        self.geometry("600x600") 
        self.resizable(False, False)

        self._criar_widgets()
        
        # Configuração modal
        self.transient(parent)
        self.grab_set()
        parent.wait_window(self)

    def _criar_widgets(self):
        frame = ttk.Frame(self, padding="10")
        frame.pack(expand=True, fill='both')

        # Cria a área de texto rolável
        self.text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=30, width=80)
        self.text_area.pack(expand=True, fill='both', pady=(0, 10))

        # --- Define "tags" para formatação (ex: negrito) ---
        self.text_area.tag_configure("header", font=("Arial", 14, "bold"), spacing3=10)
        self.text_area.tag_configure("sub_header", font=("Arial", 12, "bold"), spacing3=5)
        self.text_area.tag_configure("code", font=("Courier New", 10), background="#f0f0f0")

        # --- Insere o Texto de Ajuda ---
        self._popular_texto_ajuda()

        # Torna o texto "somente leitura"
        self.text_area.config(state='disabled')

        # Botão para fechar
        btn_fechar = ttk.Button(frame, text="Fechar", command=self.destroy)
        btn_fechar.pack(side='bottom')

    def _popular_texto_ajuda(self):
        """Preenche a caixa de texto com o guia."""
        
        self.text_area.insert(tk.END, "Guia do Formato de Arquivo\n", "header")
        self.text_area.insert(tk.END, 
            "O arquivo de configuração deve ser um .txt simples.\n\n"
        )

        # --- 1. Linha do Sistema ---
        self.text_area.insert(tk.END, "Linha 1: Configuração do Sistema\n", "sub_header")
        self.text_area.insert(tk.END, "Formato: \n", "code")
        self.text_area.insert(tk.END, "algoritmo_escalonamento;quantum\n", "code")
        self.text_area.insert(tk.END, 
            "\nExemplo:\n", "code")
        self.text_area.insert(tk.END, "SRTF;4\n\n", "code")
        self.text_area.insert(tk.END, 
            "Algoritmos Válidos: FCFS, PRIOP, SRTF.\n"
            "Quantum: Um número inteiro (ex: 4). Usado apenas por algoritmos preemptivos.\n\n"
        )

        # --- 2. Linhas de Tarefa ---
        self.text_area.insert(tk.END, "Linhas 2..N: Definição de Tarefas\n", "sub_header")
        self.text_area.insert(tk.END, "Formato: \n", "code")
        self.text_area.insert(tk.END, "id;cor;ingresso;duracao;prioridade;lista_eventos\n\n", "code")
        
        self.text_area.insert(tk.END, 
            "id: Identificador (ex: t01).\n"
            "cor: ID numérico da cor.\n"
            "ingresso: Tick de relógio que a tarefa entra no sistema (ex: 0).\n"
            "duracao: Duração total de execução da tarefa (ex: 5).\n"
            "prioridade: Prioridade (ex: 1). (Usado por PRIOP).\n"
            "lista_eventos: Lista de eventos (detalhes abaixo).\n\n"
        )

        # --- 3. Lista de Eventos ---
        self.text_area.insert(tk.END, "Formato da 'lista_eventos'\n", "sub_header")
        self.text_area.insert(tk.END, 
            "A lista é opcional. Se vazia, não inclua nada após a prioridade.\n"
            "Múltiplos eventos são separados por |\n"
            "Cada evento tem o formato: (tipo,ingresso_evento,param1,param2,...)\n\n"
        )
        self.text_area.insert(tk.END, "Tipos de Eventos Válidos:\n", "code")
        self.text_area.insert(tk.END, "  IO: (IO, ingresso, duracao)\n", "code")
        self.text_area.insert(tk.END, "  Mutex Lock: (ML, ingresso, id_mutex)\n", "code")
        self.text_area.insert(tk.END, "  Mutex Unlock: (MU, ingresso, id_mutex)\n", "code")
        self.text_area.insert(tk.END, "  Envio: (SND, ingresso)\n", "code")
        self.text_area.insert(tk.END, "  Recebimento: (RCV, ingresso)\n\n", "code")
        self.text_area.insert(tk.END, 
            "Exemplo de linha de tarefa COM eventos:\n", "code")
        self.text_area.insert(tk.END, "t01;0;0;10;1;(IO,2,3)|(ML,6,M1)|(MU,8,M1)\n", "code")
        self.text_area.insert(tk.END, 
            "(Tarefa t01, cor 0, ingresso 0, duração 10, prio 1, com I/O no tempo 2, Lock no tempo 6, Unlock no tempo 8)\n\n"
        )

        # --- 4. IDs de Cores ---
        self.text_area.insert(tk.END, "IDs de Cores Válidos\n", "sub_header")
        cores_formatadas = "\n".join(get_lista_cores_para_combobox())
        self.text_area.insert(tk.END, cores_formatadas)