import tkinter as tk
from tkinter import ttk, messagebox
from .modalEvento import ModalEvent
from .cores import get_lista_cores_para_combobox, extrair_id_cor_do_texto, get_cor_nome
class ModalTarefas(tk.Toplevel):
    """Modal para adicionar/editar tarefas."""
    def __init__(self, parent, dados_tarefa_existente=None):
        """Inicializa o modal de tarefa."""
        super().__init__(parent) # inicializa a janela pai
        self.dados_existentes = dados_tarefa_existente # dados da tarefa se for edição
        # se dados_tarefa_existente for None, é uma nova tarefa. Se não, é edição.
        titulo = "Editar Tarefa" if self.dados_existentes else "Adicionar Nova Tarefa"
        self.title(titulo) # título dinâmico
        
        self.resultado = None # resultado final do modal (dados da tarefa ou None)

        # Lista de eventos associados à tarefa
        self.eventos = list(self.dados_existentes.get('eventos', [])) if self.dados_existentes else []

        defaults = dados_tarefa_existente or {} # usa dados existentes ou vazio

        # Variáveis para os campos da tarefa
        # cor, ingresso, duração, prioridade
        self.cor_tarefa_var = tk.StringVar(value=f"{defaults.get('cor', 1)}: {get_cor_nome(defaults.get('cor', 1))}") # cor padrão
        self.ingresso_tarefa_var = tk.IntVar(value=defaults.get('ingresso', 0)) # ingresso padrão 0
        self.duracao_tarefa_var = tk.IntVar(value=defaults.get('duracao', 5)) # duração padrão 5
        self.prioridade_tarefa_var = tk.IntVar(value=defaults.get('prioridade', 1)) # prioridade padrão 1
        
        self.criar_widgets() # cria os widgets da interface

        self._atualizar_lista_eventos_ui() # popula a lista de eventos na UI

        # --- Lógica Modal ---
        self.transient(parent) # Torna a janela modal em relação à janela pai
        self.grab_set() # Captura todos os eventos para esta janela       
        parent.wait_window(self)  # Espera até fechar esta modal

    def criar_widgets(self):
        """Cria todos os widgets da interface."""
        frame = ttk.Frame(self, padding="10") # frame principal
        frame.pack(expand=True, fill='both') # expande para preencher a janela

        # Campos para definir atributos da tarefa
        ttk.Label(frame, text="Cor da Tarefa:").pack(anchor='w', pady=(10, 5)) # label da cor
        # Combobox de cores
        self.cor_combobox = ttk.Combobox(
            frame, 
            textvariable=self.cor_tarefa_var,
            values=get_lista_cores_para_combobox(), 
            state="readonly"
        )
        self.cor_combobox.pack(fill='x') # empacota o combobox

        # Label e campo de entrada para o tempo de ingresso
        ttk.Label(frame, text="Tempo de Ingresso:").pack(anchor='w', pady=(10, 5))
        ttk.Entry(frame, textvariable=self.ingresso_tarefa_var).pack(fill='x')

        # Label e campo de entrada para a duração da tarefa
        ttk.Label(frame, text="Duração da Tarefa:").pack(anchor='w', pady=(10, 5))
        ttk.Entry(frame, textvariable=self.duracao_tarefa_var).pack(fill='x')

        # Label e campo de entrada para a prioridade da tarefa
        ttk.Label(frame, text="Prioridade da Tarefa:").pack(anchor='w', pady=(10, 5))
        ttk.Entry(frame, textvariable=self.prioridade_tarefa_var).pack(fill='x')

        # --- Botão para chamar a Modal para Eventos das Tarefas ---
        ttk.Button(
            frame, 
            text="Adicionar Evento", 
            command=self._abrir_modal_evento
        ).pack(pady=(10, 0))

        # Botão para remover todos os eventos
        ttk.Button(
            frame,
            text="Remover Todas as Eventos...",
            command=self._remover_todos_eventos
        ).pack(pady=(5, 10))

        # --- Mostrar os eventos adicionados ---

        event_frame = ttk.LabelFrame(frame, text="Eventos", padding=10)
        event_frame.pack(expand=True, fill='both', pady=10)

        event_frame.columnconfigure(0, weight=1)
        event_frame.rowconfigure(0, weight=1)

        self.lista_eventos = tk.Listbox(event_frame, width=50)
        self.lista_eventos.grid(row=0, column=0, sticky='nsew')

        # botões Editar e Remover
        event_btn_frame = ttk.Frame(event_frame)
        event_btn_frame.grid(row=0, column=1, sticky='n')
        ttk.Button(
            event_btn_frame,
            text="Editar...",
            command=self._editar_evento
        ).pack(pady=5, fill='x')

        ttk.Button(
            event_btn_frame,
            text="Remover",
            command=self._remover_evento
        ).pack(pady=5, fill='x')

        # --- Botões de Salvar/Cancelar ---
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=(20, 0))
        
        ttk.Button(btn_frame, text="Salvar", command=self._on_salvar).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self._on_cancelar).pack(side='left', padx=5)

    def _abrir_modal_evento(self):
        """Abre a modal para adicionar um novo evento."""
        modal_evento = ModalEvent(self, dados_evento_existente=None) # nova evento
        if modal_evento.resultado: # se um evento foi criado
            evento = modal_evento.resultado # obtém os dados do evento
            if not hasattr(self, 'eventos'): # se a lista de eventos não existir
                self.eventos = [] # inicializa a lista de eventos
            self.eventos.append(evento) # adiciona o evento à lista
            
            self._atualizar_lista_eventos_ui() # atualiza a lista na UI

    def _atualizar_lista_eventos_ui(self):
        """Atualiza a lista de eventos na interface."""
        self.lista_eventos.delete(0, 'end') # limpa a lista atual
        
        # Mapa para converter 'IO' de volta para 'I/O'
        mapa_tipos_display = {
            "IO": "I/O", 
            "ML": "Mutex Lock", 
            "MU": "Mutex Unlock", 
            "SND": "Envio", 
            "RCV": "Recebimento"
        }

        for evento in self.eventos: # itera sobre os eventos
            tipo_abrev = evento.get('tipo_evento', 'N/A') # obtém o tipo abreviado
            tipo_display = mapa_tipos_display.get(tipo_abrev, tipo_abrev) # converte para display
            tempo_ini = evento.get('instante', '?') # obtém o instante inicial
            dur = evento.get('duracao', '?') # obtém a duração

            display_text = f"[{tipo_display}] Início: {tempo_ini}, Duração: {dur}" # texto padrão

            if tipo_abrev != "IO": # para tipos sem duração
                display_text = f"[{tipo_display}] Início: {tempo_ini}" # texto sem duração

            self.lista_eventos.insert('end', display_text) # insere na lista
    
    def _editar_evento(self):
        """Abre a modal para editar um evento existente."""
        indices_selecionados = self.lista_eventos.curselection() # obtém o índice selecionado
        if not indices_selecionados: # se nada estiver selecionado
            messagebox.showwarning("Atenção", "Selecione um evento para editar.", parent=self)
            return
            
        indice = indices_selecionados[0] # obtém o índice
        evento_para_editar = self.eventos[indice] # obtém os dados do evento

        modal_evento = ModalEvent(self, dados_evento_existente=evento_para_editar) # abre a modal para editar
        
        if modal_evento.resultado: #' se o evento foi editado
            self.eventos[indice] = modal_evento.resultado # atualiza o evento na lista
            self._atualizar_lista_eventos_ui() # atualiza a lista na UI
    
    def _remover_evento(self):
        """Remove o evento selecionado da lista."""
        indices_selecionados = self.lista_eventos.curselection() # obtém o índice selecionado
        if not indices_selecionados: # se nada estiver selecionado
            messagebox.showwarning("Atenção", "Selecione um evento para remover.", parent=self)
            return
            
        indice = indices_selecionados[0] # obtém o índice
        
        # Confirmação de remoção
        if not messagebox.askyesno("Confirmar", f"Tem certeza que deseja remover o evento selecionado?", parent=self):
            return

        self.eventos.pop(indice) # remove o evento da lista
        self._atualizar_lista_eventos_ui() # atualiza a lista na UI

    def _remover_todos_eventos(self):
        """Remove todos os eventos da lista."""
        if not self.eventos: # se a lista já estiver vazia
            messagebox.showinfo("Info", "Não há eventos para remover.", parent=self)
            return

        # confirmação de remoção
        if not messagebox.askyesno("Confirmar", "Tem certeza que deseja remover todos os eventos?", parent=self):
            return

        self.eventos.clear() # limpa a lista de eventos
        self._atualizar_lista_eventos_ui() # atualiza a lista na UI

    def _on_salvar(self):
        """Salva os dados da tarefa e eventos."""
        # Chama a função de validação
        valido, dados_ou_erro = self._validar_tarefa_e_eventos()
        
        if not valido:
            # Se falhar, mostra o erro e não fecha
            messagebox.showerror("Erro de Validação", dados_ou_erro, parent=self)
            return

        # Se for válido, 'dados_ou_erro' contém os dados prontos
        self.resultado = dados_ou_erro # armazena o resultado
        self.destroy() # fecha o modal

    def _validar_tarefa_e_eventos(self):
        """
        Função única que valida a tarefa e sua lista de eventos.
        """
        try:
            # --- Validação dos campos da Tarefa ---
            duracao_tarefa = self.duracao_tarefa_var.get()
            ingresso_tarefa = self.ingresso_tarefa_var.get()
            prioridade_tarefa = self.prioridade_tarefa_var.get()
            cor_id = extrair_id_cor_do_texto(self.cor_tarefa_var.get())

            if duracao_tarefa <= 0: # duração deve ser maior que 0
                return (False, "A 'Duração da Tarefa' deve ser maior que 0.")
            if ingresso_tarefa < 0: # tempo de ingresso não pode ser negativo
                return (False, "O 'Tempo de Ingresso' da tarefa não pode ser negativo.")
            if prioridade_tarefa <= 0: # prioridade deve ser maior que 0
                return (False, "A 'Prioridade da Tarefa' deve ser maior que 0.")

            # --- Validações da lista de Eventos (chamando os auxiliares) ---
            valido, msg = self._validar_pares_mutex() # valida pares de Mutex Lock/Unlock
            if not valido:
                return (False, msg)

            valido, msg = self._validar_sobreposicao_eventos() # valida sobreposição de eventos
            if not valido:
                return (False, msg)

            valido, msg = self._validar_limites_eventos(duracao_tarefa) # valida limites dos eventos
            if not valido:
                return (False, msg)

            # --- Se tudo estiver válido, constrói o dicionário final ---
            dados_finais = {
                "cor": cor_id,
                "ingresso": ingresso_tarefa,
                "duracao": duracao_tarefa,
                "prioridade": prioridade_tarefa,
                "eventos": self.eventos
            }
            return (True, dados_finais) # retorna sucesso com os dados

        except tk.TclError as e: # trata erros de conversão
            return (False, f"Dado inválido: {e}\nCertifique-se que os campos da tarefa são números.")
        except Exception as e: # trata erros inesperados
            return (False, f"Ocorreu um erro inesperado: {e}")

    def _validar_pares_mutex(self):
        """Valida a lógica de Lock/Unlock."""
        mutexes_abertos = {} # dicionário para rastrear mutexes travados
        try:
            eventos_ordenados = sorted(self.eventos, key=lambda ev: ev['instante']) # ordena os eventos pelo instante
        except KeyError:
            return (False, "Um evento está sem 'instante inicial'.") # erro se algum evento não tiver instante

        for evento in eventos_ordenados: # itera sobre os eventos ordenados
            tipo = evento.get('tipo_evento') # obtém o tipo do evento
            mid = evento.get('mutex_id') # obtém o ID do mutex
            tempo = evento.get('instante') # obtém o instante do evento

            if tipo == "ML": # Mutex Lock
                if mid in mutexes_abertos: # já está travado
                    return (False, f"Erro Lógico: Mutex '{mid}' foi travado 2 vezes (em {mutexes_abertos[mid]} e {tempo}).")
                mutexes_abertos[mid] = tempo # marca como travado
            elif tipo == "MU": # Mutex Unlock
                if mid not in mutexes_abertos: # não estava travado
                    return (False, f"Erro Lógico: Mutex '{mid}' foi liberado em {tempo} sem ser travado.")
                del mutexes_abertos[mid]
        
        if mutexes_abertos:
            mid_aberto = list(mutexes_abertos.keys())[0] # pega um mutex que ficou aberto
            return (False, f"Erro Lógico: Mutex '{mid_aberto}' foi travado mas nunca liberado.")
        return (True, "OK")

    def _validar_sobreposicao_eventos(self):
        """Valida sobreposição de eventos."""
        if not self.eventos: # se não houver eventos
            return (True, "OK")
            
        try:
            eventos_ordenados = sorted(self.eventos, key=lambda ev: ev['instante']) # ordena os eventos pelo instante
        except KeyError:
            return (False, "Um evento está sem 'instante inicial'.") # erro se algum evento não tiver instante

        ultimo_tempo_fim = -1 # inicializa o tempo fim do último evento
        
        for evento in eventos_ordenados: # itera sobre os eventos ordenados
            tempo_inicio = evento['instante'] # obtém o instante inicial
            # Eventos sem duração (ML, MU) têm duração 0
            duracao = evento.get('duracao', 0) # obtém a duração (0 se não existir)
            
            if tempo_inicio < ultimo_tempo_fim: # verifica sobreposição
                return (False, f"Erro de Sobreposição: Evento '{evento.get('tipo_evento')}' em {tempo_inicio} começa antes do evento anterior terminar em {ultimo_tempo_fim}.")
            
            ultimo_tempo_fim = tempo_inicio + duracao # atualiza o tempo fim do último evento
            
        return (True, "OK")

    def _validar_limites_eventos(self, duracao_tarefa):
        """Valida se os eventos estão dentro da duração da tarefa."""
        if not self.eventos:
            return (True, "OK") # sem eventos, nada a validar

        for evento in self.eventos: # itera sobre os eventos
            try:
                tempo_inicio = evento['instante'] # obtém o instante inicial
                duracao = evento.get('duracao', 0) # obtém a duração (0 se não existir)
                tempo_fim = tempo_inicio + duracao # calcula o tempo final
                
                if tempo_fim > duracao_tarefa: # verifica se ultrapassa a duração da tarefa
                    return (False, f"Erro de Limite: Evento '{evento.get('tipo_evento')}' (Início: {tempo_inicio}, Dur: {duracao}) termina em {tempo_fim}, que é maior que a duração da tarefa ({duracao_tarefa}).")
            except Exception as e: # trata erros inesperados
                return (False, f"Erro ao processar evento: {e}")
                
        return (True, "OK") 

    def _on_cancelar(self):
        """Cancela a operação e fecha o modal."""
        self.resultado = None # nenhum resultado
        self.destroy() # fecha o modal
