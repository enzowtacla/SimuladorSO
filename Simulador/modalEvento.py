import tkinter as tk
from tkinter import ttk, messagebox

class ModalEvent(tk.Toplevel):
    def __init__(self, parent, dados_evento_existente=None):
        super().__init__(parent)
        self.dados_existentes = dados_evento_existente
        titulo = "Editar Evento" if self.dados_existentes else "Adicionar Novo Evento"
        self.title(titulo)
        
        self.resultado = None

        defaults = dados_evento_existente or {}

        mapa_tipos_reverso = {
                    "IO": "I/O", 
                    "ML": "Mutex Lock", 
                    "MU": "Mutex Unlock", 
                    "SND": "Envio", 
                    "RCV": "Recebimento"
                }

        tipo_abrev_padrao = defaults.get('tipo_evento', 'IO')
        self.tipo_display_padrao = mapa_tipos_reverso.get(tipo_abrev_padrao, "I/O")
        self.tipo_var = tk.StringVar(value=self.tipo_display_padrao)

        # variaveis dinâmicas a depender do tipo de evento
        self.dynamic_vars = {}

        # Chamar a criação da interface
        self._criar_widgets()

        # função para popular os campos com base no tipo
        self._on_event_type_changed()

        # Configurar a lógica da modal
        self.transient(parent)
        self.grab_set()
        parent.wait_window(self)
        
    def _criar_widgets(self):
        """Toda a criação da interface vai aqui."""
        frame = ttk.Frame(self, padding="10")
        frame.pack(fill='both', expand=True)

        # campos para evento

        ttk.Label(frame, text="Tipo:").pack(anchor='w', pady=(0, 5))
        tipos_de_evento = ["I/O", "Mutex Lock", "Mutex Unlock", "Envio", "Recebimento"]
        
        combo = ttk.Combobox(
            frame, 
            textvariable=self.tipo_var,
            values=tipos_de_evento,
            state="readonly"
        )
        combo.pack(fill='x', pady=(0, 10))

        combo.bind("<<ComboboxSelected>>", self._on_event_type_changed)

        # --- 2. Frame Dinâmico (Placeholder) ---
        self.dynamic_frame = ttk.Frame(frame, padding=10, relief="groove", borderwidth=1)
        self.dynamic_frame.pack(fill='both', expand=True)

        # Botões
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(side='bottom', pady=(15, 0))
        
        ttk.Button(btn_frame, text="Salvar Evento", command=self._on_salvar).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self._on_cancelar).pack(side='left', padx=5)

        combo.focus_set()

    def _on_event_type_changed(self, event=None):
        for widget in self.dynamic_frame.winfo_children():
            widget.destroy()
        self.dynamic_vars.clear()

        tipo = self.tipo_var.get()
        defaults = self.dados_existentes or {}
        # --- Cria os novos widgets com base no tipo e preenche com dados ---
        if tipo == "I/O":
            var_ing = tk.IntVar(value=defaults.get('instante', 0))
            var_dur = tk.IntVar(value=defaults.get('duracao', 1))
            self.dynamic_vars = {'instante': var_ing, 'duracao': var_dur}

            ttk.Label(self.dynamic_frame, text="Instante inicial:").pack(anchor='w')
            ttk.Entry(self.dynamic_frame, textvariable=var_ing).pack(fill='x', pady=5)
            ttk.Label(self.dynamic_frame, text="Duração do I/O:").pack(anchor='w')
            ttk.Entry(self.dynamic_frame, textvariable=var_dur).pack(fill='x', pady=5)

        elif tipo in ["Mutex Lock", "Mutex Unlock"]:
            var_ing = tk.IntVar(value=defaults.get('instante', 0))
            var_mid = tk.StringVar(value=defaults.get('mutex_id', 'M1'))
            self.dynamic_vars = {'instante': var_ing, 'mutex_id': var_mid}

            ttk.Label(self.dynamic_frame, text="Instante inicial:").pack(anchor='w')
            ttk.Entry(self.dynamic_frame, textvariable=var_ing).pack(fill='x', pady=5)
            label_text = f"ID do Mutex (ex: M1, M2):"
            ttk.Label(self.dynamic_frame, text=label_text).pack(anchor='w')
            ttk.Entry(self.dynamic_frame, textvariable=var_mid).pack(fill='x', pady=5)

        elif tipo in ["Envio", "Recebimento"]:
            var_ing = tk.IntVar(value=defaults.get('instante', 0))
            self.dynamic_vars = {'instante': var_ing}
            ttk.Label(self.dynamic_frame, text="Instante inicial:").pack(anchor='w')
            ttk.Entry(self.dynamic_frame, textvariable=var_ing).pack(fill='x', pady=5)
        
        else:
            if not tipo:
                ttk.Label(self.dynamic_frame, text="Selecione um tipo de evento acima.").pack()

    def _on_salvar(self):
        # 1. Chama a função de validação única
        valido, dados_ou_erro = self._validar_e_coletar_dados()
        
        if not valido:
            # 2. Se falhar, mostra o erro e não fecha
            messagebox.showerror("Erro de Validação", dados_ou_erro, parent=self)
            return

        # 3. Se for válido, 'dados_ou_erro' contém os dados prontos
        self.resultado = dados_ou_erro
        self.destroy()

    def _validar_e_coletar_dados(self):
        """
        Função única que valida tudo.
        Retorna (True, dados) em sucesso.
        Retorna (False, "mensagem de erro") em falha.
        """
        try:
            tipo_evento_display = self.tipo_var.get()
            if not tipo_evento_display:
                return (False, "Tipo do evento não pode ser vazio")

            # Coleta os dados brutos das variáveis dinâmicas
            dados_brutos = {}
            for nome_var, var_obj in self.dynamic_vars.items():
                dados_brutos[nome_var] = var_obj.get()

            # --- Validações ---
            instante = dados_brutos.get('instante')
            if instante is not None and instante < 0:
                return (False, "O 'Instante inicial' não pode ser negativo.")

            if tipo_evento_display == "I/O":
                if dados_brutos.get('duracao', 0) <= 0:
                    return (False, "A 'Duração do I/O' deve ser maior que 0.")
            
            if tipo_evento_display in ["Mutex Lock", "Mutex Unlock"]:
                if not dados_brutos.get('mutex_id', '').strip():
                    return (False, "O 'ID do Mutex' não pode ser vazio.")
            # --- Fim Validações ---

            # Mapeia o tipo
            tipo_evento_abrev = "IO" if tipo_evento_display == "I/O" else "ML" if tipo_evento_display == "Mutex Lock" else "MU" if tipo_evento_display == "Mutex Unlock" else "SND" if tipo_evento_display == "Envio" else "RCV"
            
            # Constrói o resultado
            resultado_final = { "tipo_evento": tipo_evento_abrev }
            resultado_final.update(dados_brutos) # Adiciona todos os dados dinâmicos

            return (True, resultado_final) 
        
        except tk.TclError as e:
            return (False, f"Dado inválido: {e}\nCertifique-se que os campos são números.")
        except Exception as e:
            return (False, f"Ocorreu um erro ao salvar o evento: {e}")
        
    def _on_cancelar(self):
        self.resultado = None
        self.destroy()