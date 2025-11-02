import tkinter as tk
from tkinter import ttk, messagebox
from .modalTarefa import ModalTarefas

class ModalConfigManual(tk.Toplevel):
    
    def __init__(self, parent, configuracao_existente=None):
        # Chamar o construtor do Toplevel
        super().__init__(parent)
        
        self.title("Configuração Manual")

        self.configuracao_existente = configuracao_existente
        self.resultado = None  # Para armazenar o resultado da configuração
        self.tipo_escalonador = self.configuracao_existente.get('tipo_escalonador', 'FCFS') if self.configuracao_existente else "FCFS"
        self.quantum = self.configuracao_existente.get('quantum', 4) if self.configuracao_existente else 4
        self.tarefas_default = [{"id": "t01", "cor": 0, "ingresso": 0, "duracao": 5, "prioridade": 1}, 
                        {"id": "t02", "cor": 1, "ingresso": 2, "duracao": 3, "prioridade": 2}, 
                        {"id": "t03", "cor": 2, "ingresso": 4, "duracao": 4, "prioridade": 1}]
        # define uma configuração padrão de tarefas
        self.tarefas = self.configuracao_existente.get('tarefas', self.tarefas_default) if self.configuracao_existente else self.tarefas_default

        # Criar a interface interna
        self._criar_widgets()

        self._atualizar_lista_tarefas_ui()
        
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
        self.tipo_escalonador = tk.StringVar(value=self.tipo_escalonador)
        escalonador_menu = ttk.Combobox(
            frame, 
            textvariable=self.tipo_escalonador,
            values=["FCFS", "PRIOP", "SRTF"], 
            state="readonly"
        )
        escalonador_menu.pack(pady=5, padx=10, fill="x")

        ttk.Label(frame, text="Quantum:").pack(pady=5)
        self.quantum = tk.IntVar(value=self.quantum)
        ttk.Entry(frame, textvariable=self.quantum).pack(pady=5, padx=10, fill="x")

        # --- Botão para chamar a Modal das Tarefas ---
        ttk.Button(
            frame, 
            text="Adicionar Tarefa", 
            command=self._abrir_modal_tarefas
        ).pack(pady=(10, 0))

        ttk.Button(
            frame,
            text="Remover Todas as Tarefas...",
            command=self._remover_todas_tarefas
        ).pack(pady=(5, 10))
        # --- Mostrar as tarefas adicionadas ---

        task_frame = ttk.LabelFrame(frame, text="Conjunto de Tarefas")
        task_frame.pack(expand=True, fill='both', padx=5, pady=10)

        task_frame.columnconfigure(0, weight=1)
        task_frame.rowconfigure(0, weight=1)

        self.lista_tarefas = tk.Listbox(task_frame, width=50)
        self.lista_tarefas.grid(row=0, column=0, sticky='nsew')

         # Frame para os botões Editar e Remover
        task_btn_frame = ttk.Frame(task_frame)
        task_btn_frame.grid(row=0, column=1, sticky='n')
        ttk.Button(
            task_btn_frame,
            text="Editar...",
            command=self._editar_tarefa
        ).pack(pady=5, fill='x')

        ttk.Button(
            task_btn_frame,
            text="Remover",
            command=self._remover_tarefa
        ).pack(pady=5, fill='x')

        # --- Botões de Salvar/Cancelar ---
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=(10, 0), side='bottom')
        
        ttk.Button(btn_frame, text="Salvar", command=self._on_salvar).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self._on_cancelar).pack(side='left', padx=5)

    def _abrir_modal_tarefas(self):

        modal_tarefas = ModalTarefas(self, dados_tarefa_existente=None)
        if modal_tarefas.resultado:
            tarefa_data = modal_tarefas.resultado
            # adicionar a tarefa à lista de tarefas
            if not hasattr(self, 'tarefas'):
                self.tarefas = []
            self.tarefas.append(tarefa_data)
            self._atualizar_lista_tarefas_ui()

    # função para atualizar a Listbox de tarefas

    def _atualizar_lista_tarefas_ui(self):
        self.lista_tarefas.delete(0, 'end')
        
        for i, tarefa_data in enumerate(self.tarefas):
            novo_id = f"t{i + 1:02d}"
            tarefa_data['id'] = novo_id 
            
            display_text = (
                f"{novo_id}: "
                f"Ingr: {tarefa_data.get('ingresso', 'N/A')}, "
                f"Dur: {tarefa_data.get('duracao', 'N/A')}, "
                f"Prio: {tarefa_data.get('prioridade', 'N/A')}, "
                f"Eventos: {len(tarefa_data.get('eventos', []))}"
            )
            self.lista_tarefas.insert('end', display_text)

    # funções para editar e remover tarefas
    def _editar_tarefa(self):
        indices_selecionados = self.lista_tarefas.curselection()
        if not indices_selecionados:
            messagebox.showwarning("Atenção", "Selecione uma tarefa para editar.", parent=self)
            return
            
        indice = indices_selecionados[0]
        tarefa_para_editar = self.tarefas[indice] 

        modal_tarefas = ModalTarefas(self, dados_tarefa_existente=tarefa_para_editar)
        
        if modal_tarefas.resultado:
            self.tarefas[indice] = modal_tarefas.resultado 
            self._atualizar_lista_tarefas_ui()

    def _remover_tarefa(self):
        indices_selecionados = self.lista_tarefas.curselection()
        if not indices_selecionados:
            messagebox.showwarning("Atenção", "Selecione uma tarefa para remover.", parent=self)
            return
            
        indice = indices_selecionados[0]
        
        tarefa_id = self.tarefas[indice].get('id', 'Tarefa')
        if not messagebox.askyesno("Confirmar", f"Tem certeza que deseja remover a tarefa {tarefa_id}?", parent=self):
            return

        self.tarefas.pop(indice)
        self._atualizar_lista_tarefas_ui()

    def _remover_todas_tarefas(self):
        if not self.tarefas:
            messagebox.showinfo("Info", "Não há tarefas para remover.", parent=self)
            return

        if not messagebox.askyesno("Confirmar", "Tem certeza que deseja remover todas as tarefas?", parent=self):
            return

        self.tarefas.clear()
        self._atualizar_lista_tarefas_ui()

    # Funções _on_salvar e _on_cancelar 
    def _on_salvar(self):
        valido, dados_ou_erro = self._validar_configuracao_global()
        
        if not valido:
            messagebox.showerror("Erro de Configuração", dados_ou_erro, parent=self)
            return

        self.resultado = dados_ou_erro
        self.destroy()

    def _validar_configuracao_global(self):
        """
        Função única que valida toda a configuração.
        """
        try:

            if self.quantum.get() <= 0:
                return (False, "O Quantum deve ser maior que 0.")
            
            if not self.tarefas:
                messagebox.showwarning("Aviso", "Nenhuma tarefa foi adicionada. Salvando configuração vazia.")

            dados_finais = {
                "tipo_escalonador": self.tipo_escalonador.get(),
                "quantum": self.quantum.get(),
                "tarefas": self.tarefas
            }
            return (True, dados_finais)
            
        except tk.TclError as e:
            return (False, f"Quantum inválido: {e}")
        except Exception as e:
            return (False, f"Ocorreu um erro: {e}")

    def _on_cancelar(self):
        self.resultado = None
        self.destroy()

