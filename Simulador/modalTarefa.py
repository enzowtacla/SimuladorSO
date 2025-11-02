import tkinter as tk
from tkinter import ttk, messagebox
from .modalEvento import ModalEvent

class ModalTarefas(tk.Toplevel):
    
    def __init__(self, parent, dados_tarefa_existente=None):
        super().__init__(parent)
        self.dados_existentes = dados_tarefa_existente
        titulo = "Editar Tarefa" if self.dados_existentes else "Adicionar Nova Tarefa"
        self.title(titulo)
        
        self.resultado = None
        self.eventos = list(self.dados_existentes.get('eventos', [])) if self.dados_existentes else []

        defaults = dados_tarefa_existente or {}
        
        self.cor_tarefa_var = tk.IntVar(value=defaults.get('cor', 1))
        self.ingresso_tarefa_var = tk.IntVar(value=defaults.get('ingresso', 0))
        self.duracao_tarefa_var = tk.IntVar(value=defaults.get('duracao', 5))
        self.prioridade_tarefa_var = tk.IntVar(value=defaults.get('prioridade', 1))

        # Criar a interface interna
        
        self.criar_widgets()

        self._atualizar_lista_eventos_ui()

        # --- Lógica Modal ---
        self.transient(parent)  
        self.grab_set()              
        parent.wait_window(self)  # Espera até fechar esta modal

    def criar_widgets(self):

        frame = ttk.Frame(self, padding="10")
        frame.pack(expand=True, fill='both')

        # Campos para definir atributos da tarefa

        ttk.Label(frame, text="Cor da Tarefa (Índice):").pack(anchor='w', pady=(10, 5))
        ttk.Entry(frame, textvariable=self.cor_tarefa_var).pack(fill='x')

        ttk.Label(frame, text="Tempo de Ingresso:").pack(anchor='w', pady=(10, 5))
        ttk.Entry(frame, textvariable=self.ingresso_tarefa_var).pack(fill='x')

        ttk.Label(frame, text="Duração da Tarefa:").pack(anchor='w', pady=(10, 5))
        ttk.Entry(frame, textvariable=self.duracao_tarefa_var).pack(fill='x')

        ttk.Label(frame, text="Prioridade da Tarefa:").pack(anchor='w', pady=(10, 5))
        ttk.Entry(frame, textvariable=self.prioridade_tarefa_var).pack(fill='x')

        # --- Botão para chamar a Modal para Eventos das Tarefas ---
        ttk.Button(
            frame, 
            text="Adicionar Evento", 
            command=self._abrir_modal_evento
        ).pack(pady=(10, 0))

        # --- Mostrar os eventos adicionados ---

        ttk.Button(
            frame,
            text="Remover Todas as Eventos...",
            command=self._remover_todos_eventos
        ).pack(pady=(5, 10))

        # --- Mostrar os eventos adicionados ---

        event_frame = ttk.LabelFrame(frame, text="Eventos", padding=10)
        event_frame.pack(expand=True, fill='both', pady=10)

        self.lista_eventos = tk.Listbox(event_frame)
        self.lista_eventos.pack(expand=True, fill='both', pady=(5, 0))
        event_btn_frame = ttk.Frame(event_frame)
        event_btn_frame.pack(side='right', fill='y')
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
        modal_evento = ModalEvent(self, dados_evento_existente=None) 
        if modal_evento.resultado:
            evento = modal_evento.resultado
            if not hasattr(self, 'eventos'):
                self.eventos = []
            self.eventos.append(evento)
            
            self._atualizar_lista_eventos_ui()

    def _atualizar_lista_eventos_ui(self):
        self.lista_eventos.delete(0, 'end')
        
        # Mapa para converter 'IO' de volta para 'I/O'
        mapa_tipos_display = {
            "IO": "I/O", 
            "ML": "Mutex Lock", 
            "MU": "Mutex Unlock", 
            "SND": "Envio", 
            "RCV": "Recebimento"
        }

        for i, evento in enumerate(self.eventos):
            tipo_abrev = evento.get('tipo_evento', 'N/A')
            tipo_display = mapa_tipos_display.get(tipo_abrev, tipo_abrev)
            tempo_ini = evento.get('ingresso', '?')
            dur = evento.get('duracao', '?')

            display_text = f"[{tipo_display}] Ingr: {tempo_ini}, Dur: {dur}"
            
            if tipo_abrev != "IO":
                 display_text = f"[{tipo_display}] Ingr: {tempo_ini}"

            self.lista_eventos.insert('end', display_text)
    
    def _editar_evento(self):
        indices_selecionados = self.lista_eventos.curselection()
        if not indices_selecionados:
            messagebox.showwarning("Atenção", "Selecione um evento para editar.", parent=self)
            return
            
        indice = indices_selecionados[0]
        evento_para_editar = self.eventos[indice] 

        modal_evento = ModalEvent(self, dados_evento_existente=evento_para_editar)
        
        if modal_evento.resultado:
            self.eventos[indice] = modal_evento.resultado 
            self._atualizar_lista_eventos_ui()
    
    def _remover_evento(self):
        indices_selecionados = self.lista_eventos.curselection()
        if not indices_selecionados:
            messagebox.showwarning("Atenção", "Selecione um evento para remover.", parent=self)
            return
            
        indice = indices_selecionados[0]
        
        if not messagebox.askyesno("Confirmar", f"Tem certeza que deseja remover o evento selecionado?", parent=self):
            return

        self.eventos.pop(indice)
        self._atualizar_lista_eventos_ui()

    def _remover_todos_eventos(self):
        if not self.eventos:
            messagebox.showinfo("Info", "Não há eventos para remover.", parent=self)
            return

        if not messagebox.askyesno("Confirmar", "Tem certeza que deseja remover todos os eventos?", parent=self):
            return

        self.eventos.clear()
        self._atualizar_lista_eventos_ui()

    def _on_salvar(self):
        # 1. Chama a função de validação única
        valido, dados_ou_erro = self._validar_tarefa_e_eventos()
        
        if not valido:
            # 2. Se falhar, mostra o erro e não fecha
            messagebox.showerror("Erro de Validação", dados_ou_erro, parent=self)
            return
            
        # 3. Se for válido, 'dados_ou_erro' contém os dados prontos
        self.resultado = dados_ou_erro
        self.destroy()

    def _validar_tarefa_e_eventos(self):
        """
        Função única que valida a tarefa e sua lista de eventos.
        """
        try:
            # --- Validação dos campos da Tarefa ---
            duracao_tarefa = self.duracao_tarefa_var.get()
            ingresso_tarefa = self.ingresso_tarefa_var.get()
            prioridade_tarefa = self.prioridade_tarefa_var.get()

            if duracao_tarefa <= 0:
                return (False, "A 'Duração da Tarefa' deve ser maior que 0.")
            if ingresso_tarefa < 0:
                return (False, "O 'Tempo de Ingresso' da tarefa não pode ser negativo.")
            if prioridade_tarefa <= 0:
                return (False, "A 'Prioridade da Tarefa' deve ser maior que 0.")

            # --- Validações da lista de Eventos (chamando os auxiliares) ---
            valido, msg = self._validar_pares_mutex()
            if not valido:
                return (False, msg)

            valido, msg = self._validar_sobreposicao_eventos()
            if not valido:
                return (False, msg)

            valido, msg = self._validar_limites_eventos(duracao_tarefa)
            if not valido:
                return (False, msg)

            
            dados_finais = {
                "cor": self.cor_tarefa_var.get(),
                "ingresso": ingresso_tarefa,
                "duracao": duracao_tarefa,
                "prioridade": prioridade_tarefa,
                "eventos": self.eventos
            }
            return (True, dados_finais)

        except tk.TclError as e:
            return (False, f"Dado inválido: {e}\nCertifique-se que os campos da tarefa são números.")
        except Exception as e:
            return (False, f"Ocorreu um erro inesperado: {e}")

    def _validar_pares_mutex(self):
        """Valida a lógica de Lock/Unlock."""
        mutexes_abertos = {}
        try:
            eventos_ordenados = sorted(self.eventos, key=lambda ev: ev['ingresso'])
        except KeyError:
            return (False, "Um evento está sem 'ingresso'.")
        
        for evento in eventos_ordenados:
            tipo = evento.get('tipo_evento')
            mid = evento.get('mutex_id')
            tempo = evento.get('ingresso')

            if tipo == "ML": # Mutex Lock
                if mid in mutexes_abertos:
                    return (False, f"Erro Lógico: Mutex '{mid}' foi travado 2 vezes (em {mutexes_abertos[mid]} e {tempo}).")
                mutexes_abertos[mid] = tempo
            elif tipo == "MU": # Mutex Unlock
                if mid not in mutexes_abertos:
                    return (False, f"Erro Lógico: Mutex '{mid}' foi liberado em {tempo} sem ser travado.")
                del mutexes_abertos[mid]
        
        if mutexes_abertos:
            mid_aberto = list(mutexes_abertos.keys())[0]
            return (False, f"Erro Lógico: Mutex '{mid_aberto}' foi travado mas nunca liberado.")
        return (True, "OK")

    def _validar_sobreposicao_eventos(self):
        """Valida sobreposição de eventos."""
        if not self.eventos:
            return (True, "OK")
            
        try:
            eventos_ordenados = sorted(self.eventos, key=lambda ev: ev['ingresso'])
        except KeyError:
            return (False, "Um evento está sem 'ingresso'.")
        
        ultimo_tempo_fim = -1
        
        for evento in eventos_ordenados:
            tempo_inicio = evento['ingresso']
            # Eventos sem duração (ML, MU) têm duração 0
            duracao = evento.get('duracao', 0) 
            
            if tempo_inicio < ultimo_tempo_fim:
                return (False, f"Erro de Sobreposição: Evento '{evento.get('tipo_evento')}' em {tempo_inicio} começa antes do evento anterior terminar em {ultimo_tempo_fim}.")
            
            ultimo_tempo_fim = tempo_inicio + duracao
            
        return (True, "OK")

    def _validar_limites_eventos(self, duracao_tarefa):
        """Valida se os eventos estão dentro da duração da tarefa."""
        if not self.eventos:
            return (True, "OK")

        for evento in self.eventos:
            try:
                tempo_inicio = evento['ingresso']
                duracao = evento.get('duracao', 0)
                tempo_fim = tempo_inicio + duracao
                
                if tempo_fim > duracao_tarefa:
                    return (False, f"Erro de Limite: Evento '{evento.get('tipo_evento')}' (Ingr: {tempo_inicio}, Dur: {duracao}) termina em {tempo_fim}, que é maior que a duração da tarefa ({duracao_tarefa}).")
            except Exception as e:
                return (False, f"Erro ao processar evento: {e}")
                
        return (True, "OK") 

    def _on_cancelar(self):
        self.resultado = None
        self.destroy()
