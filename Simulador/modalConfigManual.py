import tkinter as tk
from tkinter import ttk, messagebox
from .modalTarefa import ModalTarefas
from .escalonadores import lista_escalonadores, indice_escalonador
class ModalConfigManual(tk.Toplevel):
    """Modal para configuração manual do simulador."""
    def __init__(self, parent, configuracao_existente=None):
        """Inicializa a modal de configuração manual."""
        # Chamar o construtor do Toplevel
        super().__init__(parent) 
        
        self.title("Configuração Manual") # Título da janela

        self.configuracao_existente = configuracao_existente # Configuração existente, se houver
        self.resultado = None  # Para armazenar o resultado da configuração
        # Valores padrão ou existentes
        self.tipo_escalonador = self.configuracao_existente.get('tipo_escalonador', 'FCFS') if self.configuracao_existente else "FCFS"
        self.quantum = self.configuracao_existente.get('quantum', 4) if self.configuracao_existente else 4
        val_env = self.configuracao_existente.get('fator_envelhecimento', 1) if self.configuracao_existente else 0
        self.fator_envelhecimento = tk.IntVar(value=val_env)

        # define uma configuração padrão de tarefas
        self.tarefas_default = [{"id": "t01", "cor": 0, "ingresso": 0, "duracao": 5, "prioridade_estatica": 1}, 
                        {"id": "t02", "cor": 1, "ingresso": 2, "duracao": 3, "prioridade_estatica": 2}, 
                        {"id": "t03", "cor": 2, "ingresso": 4, "duracao": 4, "prioridade_estatica": 1}]
        
        # carregar tarefas existentes ou padrão
        self.tarefas = self.configuracao_existente.get('tarefas', self.tarefas_default) if self.configuracao_existente else self.tarefas_default

        # Criar a interface interna
        self._criar_widgets()

        self._atualizar_lista_tarefas_ui() # popular a lista de tarefas na UI
        
        # Configurar o comportamento modal
        self.transient(parent) # Torna a janela modal em relação à janela pai
        self.grab_set() # Captura todos os eventos para esta janela

        # Faz a Janela Principal esperar por esta
        parent.wait_window(self)

    def _criar_widgets(self):
        """Cria todos os widgets da interface."""
        frame = ttk.Frame(self, padding="10")
        frame.pack(expand=True, fill='both')
        
        # seleção do tipo de escalonador
        ttk.Label(frame, text="Tipo de Escalonador:").pack(pady=5) # label do tipo de escalonador
        self.tipo_escalonador = tk.StringVar(value=self.tipo_escalonador) # variável do tipo de escalonador
        escalonador_menu = ttk.Combobox(
            frame, 
            textvariable=self.tipo_escalonador,
            values=lista_escalonadores, 
            state="readonly"
        ) # combobox do tipo de escalonador
        escalonador_menu.pack(pady=5, padx=10, fill="x")

        # dá o bind na modificação do combobox para verificar visibilidade dos campos
        escalonador_menu.bind("<<ComboboxSelected>>", self._verificar_visibilidade_campos)

        # campo do quantum
        ttk.Label(frame, text="Quantum:").pack(pady=5) # label do quantum
        self.quantum = tk.IntVar(value=self.quantum) # variável do quantum
        self.entry_quantum = ttk.Entry(frame, textvariable=self.quantum)
        self.entry_quantum.pack(pady=5, padx=10, fill="x")

        # Criamos um frame container para poder esconder/mostrar o bloco inteiro
        self.frame_envelhecimento = ttk.Frame(frame)
        
        ttk.Label(self.frame_envelhecimento, text="Fator de Envelhecimento:").pack(pady=5)
        ttk.Entry(self.frame_envelhecimento, textvariable=self.fator_envelhecimento).pack(pady=5, padx=10, fill="x")

        # --- Botão para chamar a Modal das Tarefas ---
        ttk.Button(
            frame, 
            text="Adicionar Tarefa", 
            command=self._abrir_modal_tarefas
        ).pack(pady=(10, 0))

        # --- Botão para remover todas as tarefas ---
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

        self._verificar_visibilidade_campos()

    def _verificar_visibilidade_campos(self, event=None):
        """Mostra ou esconde campos dependendo do escalonador selecionado."""
        selecao = self.tipo_escalonador.get()
        
        if selecao == lista_escalonadores[indice_escalonador["PRIOPEnv"]]:
            # mostra o frame do envelhecimento
            self.frame_envelhecimento.pack(after=self.entry_quantum, pady=5, padx=10, fill="x")
        else:
            # esconde o frame do envelhecimento
            self.frame_envelhecimento.pack_forget()

    def _abrir_modal_tarefas(self):
        """Abre o modal para adicionar/editar tarefas."""
        modal_tarefas = ModalTarefas(self, dados_tarefa_existente=None) # abre o modal de tarefas
        if modal_tarefas.resultado: # se houver resultado
            tarefa_data = modal_tarefas.resultado 
            # adicionar a tarefa à lista de tarefas
            if not hasattr(self, 'tarefas'): # se a lista de tarefas não existir
                self.tarefas = [] # inicializa a lista de tarefas
            self.tarefas.append(tarefa_data) # adiciona a nova tarefa
            self._atualizar_lista_tarefas_ui() # atualiza a lista de tarefas na UI

    def _atualizar_lista_tarefas_ui(self):
        """Atualiza a Listbox de tarefas na interface."""
        self.lista_tarefas.delete(0, 'end') # limpa a lista atual
        
        for i, tarefa_data in enumerate(self.tarefas): # itera sobre as tarefas
            novo_id = f"t{i + 1:02d}" # gera um novo ID
            tarefa_data['id'] = novo_id # atualiza o ID da tarefa
            
            display_text = (
                f"{novo_id}: "
                f"Ingr: {tarefa_data.get('ingresso', 'N/A')}, "
                f"Dur: {tarefa_data.get('duracao', 'N/A')}, "
                f"Prio: {tarefa_data.get('prioridade_estatica', 'N/A')}, "
                f"Eventos: {len(tarefa_data.get('eventos', []))}"
            ) # texto de exibição da tarefa
            self.lista_tarefas.insert('end', display_text) # insere o texto na lista

    def _editar_tarefa(self):
        """Abre o modal para editar uma tarefa existente."""
        indices_selecionados = self.lista_tarefas.curselection() # obtém o índice selecionado
        if not indices_selecionados: # se nada estiver selecionado
            messagebox.showwarning("Atenção", "Selecione uma tarefa para editar.", parent=self)
            return
            
        indice = indices_selecionados[0] # pega o índice selecionado
        tarefa_para_editar = self.tarefas[indice] # obtém os dados da tarefa

        # abre o modal de tarefas com os dados existentes
        modal_tarefas = ModalTarefas(self, dados_tarefa_existente=tarefa_para_editar) 
        
        if modal_tarefas.resultado: # se houver resultado
            self.tarefas[indice] = modal_tarefas.resultado # atualiza a tarefa na lista 
            self._atualizar_lista_tarefas_ui() # atualiza a lista de tarefas na UI

    def _remover_tarefa(self):
        """Remove a tarefa selecionada."""
        indices_selecionados = self.lista_tarefas.curselection() # obtém o índice selecionado
        if not indices_selecionados: # se nada estiver selecionado
            messagebox.showwarning("Atenção", "Selecione uma tarefa para remover.", parent=self)
            return
            
        indice = indices_selecionados[0] # pega o índice selecionado
        
        tarefa_id = self.tarefas[indice].get('id', 'Tarefa') # obtém o ID da tarefa
        # confirmação de remoção
        if not messagebox.askyesno("Confirmar", f"Tem certeza que deseja remover a tarefa {tarefa_id}?", parent=self):
            return # se não confirmar, sai da função

        self.tarefas.pop(indice) # remove a tarefa da lista
        self._atualizar_lista_tarefas_ui() # atualiza a lista de tarefas na UI

    def _remover_todas_tarefas(self):
        """Remove todas as tarefas."""
        if not self.tarefas: # se não houver tarefas
            messagebox.showinfo("Info", "Não há tarefas para remover.", parent=self)
            return

        # confirmação de remoção
        if not messagebox.askyesno("Confirmar", "Tem certeza que deseja remover todas as tarefas?", parent=self):
            return # se não confirmar, sai da função

        self.tarefas.clear() # limpa a lista de tarefas
        self._atualizar_lista_tarefas_ui() # atualiza a lista de tarefas na UI

    def _on_salvar(self):
        """Valida e salva a configuração."""
        valido, dados_ou_erro = self._validar_configuracao_global() # valida a configuração global
        
        if not valido: # se não for válido
            messagebox.showerror("Erro de Configuração", dados_ou_erro, parent=self)
            return

        self.resultado = dados_ou_erro # salva o resultado válido
        self.destroy() # fecha a janela

    def _validar_configuracao_global(self):
        """
        Função única que valida toda a configuração.
        """
        try:

            if self.quantum.get() <= 0: # validação do quantum
                return (False, "O Quantum deve ser maior que 0.")
            
            if not self.tarefas: # verifica se tarefas foram adicionadas
                messagebox.showwarning("Aviso", "Nenhuma tarefa foi adicionada. Salvando configuração vazia.")

            fator_env = 0
            if self.tipo_escalonador.get() == lista_escalonadores[indice_escalonador["PRIOPEnv"]]:
                try:
                    fator_env = self.fator_envelhecimento.get()
                    if fator_env <= 0:
                        return (False, "O Fator de Envelhecimento deve ser maior que 0.")
                except:
                     return (False, "Fator de Envelhecimento inválido.")

            dados_finais = {
                "tipo_escalonador": self.tipo_escalonador.get(),
                "quantum": self.quantum.get(),
                "fator_envelhecimento": fator_env,
                "tarefas": self.tarefas
            } # dados finais da configuração
            return (True, dados_finais) # retorna sucesso com os dados
            
        except tk.TclError as e: # trata erros de quantum
            return (False, f"Quantum inválido: {e}")
        except Exception as e: # trata erros inesperados
            return (False, f"Ocorreu um erro: {e}")

    def _on_cancelar(self):
        """Cancela a configuração e fecha a modal."""
        self.resultado = None # nenhum resultado
        self.destroy() # fecha a janela