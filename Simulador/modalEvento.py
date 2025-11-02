import tkinter as tk
from tkinter import ttk, messagebox

class ModalEvent(tk.Toplevel):
    """Modal para adicionar/editar eventos de tarefas."""
    def __init__(self, parent, dados_evento_existente=None):
        """Inicializa o modal de evento."""
        super().__init__(parent) # inicializa a janela pai
        self.dados_existentes = dados_evento_existente # dados do evento se for edição
        # se dados_evento_existente for None, é um novo evento. Se não, é edição.
        titulo = "Editar Evento" if self.dados_existentes else "Adicionar Novo Evento" # título dinâmico
        self.title(titulo)
        
        self.resultado = None # resultado final do modal (dados do evento ou None)

        defaults = dados_evento_existente or {} # usa dados existentes ou vazio

        mapa_tipos_reverso = {
                    "IO": "I/O", 
                    "ML": "Mutex Lock", 
                    "MU": "Mutex Unlock", 
                    "SND": "Envio", 
                    "RCV": "Recebimento"
                } # mapeia abreviações para nomes completos

        tipo_abrev_padrao = defaults.get('tipo_evento', 'IO') # padrão para novo evento é I/O
        self.tipo_display_padrao = mapa_tipos_reverso.get(tipo_abrev_padrao, "I/O") # converte para display
        self.tipo_var = tk.StringVar(value=self.tipo_display_padrao) # variável do tipo de evento

        # variaveis dinâmicas a depender do tipo de evento
        self.dynamic_vars = {}

        # Chamar a criação da interface
        self._criar_widgets()

        # função para popular os campos com base no tipo
        self._on_event_type_changed()

        # Configurar a lógica da modal
        self.transient(parent) # torna a janela modal em relação à janela pai
        self.grab_set() # captura todos os eventos para esta janela
        parent.wait_window(self) # espera até que a janela seja fechada
        
    def _criar_widgets(self):
        """Toda a criação da interface."""
        frame = ttk.Frame(self, padding="10") # frame principal
        frame.pack(fill='both', expand=True) # expande para preencher a janela

        # campos para evento

        ttk.Label(frame, text="Tipo:").pack(anchor='w', pady=(0, 5)) # label do tipo
        tipos_de_evento = ["I/O", "Mutex Lock", "Mutex Unlock", "Envio", "Recebimento"] # opções de tipo
        
        combo = ttk.Combobox(
            frame, 
            textvariable=self.tipo_var,
            values=tipos_de_evento,
            state="readonly"
        ) # combobox do tipo
        combo.pack(fill='x', pady=(0, 10)) # empacota o combobox

        combo.bind("<<ComboboxSelected>>", self._on_event_type_changed) # bind para mudança de seleção

        # --- 2. Frame Dinâmico (Placeholder) ---
        self.dynamic_frame = ttk.Frame(frame, padding=10, relief="groove", borderwidth=1)
        self.dynamic_frame.pack(fill='both', expand=True) # empacota o frame dinâmico

        # Botões
        btn_frame = ttk.Frame(frame) # frame para botões
        btn_frame.pack(side='bottom', pady=(15, 0)) # empacota o frame dos botões
        
        # Botões Salvar e Cancelar
        ttk.Button(btn_frame, text="Salvar Evento", command=self._on_salvar).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self._on_cancelar).pack(side='left', padx=5)

        # Foca no combobox ao abrir
        combo.focus_set()

    def _on_event_type_changed(self, event=None):
        """Atualiza os campos dinâmicos com base no tipo selecionado."""
        # Limpa o frame dinâmico atual
        for widget in self.dynamic_frame.winfo_children():
            widget.destroy() # remove todos os widgets filhos
        self.dynamic_vars.clear() # limpa as variáveis dinâmicas

        tipo = self.tipo_var.get() # obtém o tipo selecionado
        defaults = self.dados_existentes or {} # dados existentes ou vazio
        # --- Cria os novos widgets com base no tipo e preenche com dados ---
        if tipo == "I/O": # tipo I/O
            var_ing = tk.IntVar(value=defaults.get('instante', 0)) # instante padrão
            var_dur = tk.IntVar(value=defaults.get('duracao', 1)) # duração padrão
            self.dynamic_vars = {'instante': var_ing, 'duracao': var_dur} # armazena as variáveis dinâmicas

            ttk.Label(self.dynamic_frame, text="Instante inicial:").pack(anchor='w') # label instante
            ttk.Entry(self.dynamic_frame, textvariable=var_ing).pack(fill='x', pady=5) # entrada instante
            ttk.Label(self.dynamic_frame, text="Duração do I/O:").pack(anchor='w') # label duração
            ttk.Entry(self.dynamic_frame, textvariable=var_dur).pack(fill='x', pady=5) # entrada duração

        elif tipo in ["Mutex Lock", "Mutex Unlock"]: # tipo Mutex
            var_ing = tk.IntVar(value=defaults.get('instante', 0)) # instante padrão
            var_mid = tk.StringVar(value=defaults.get('mutex_id', 'M1')) # mutex id padrão
            self.dynamic_vars = {'instante': var_ing, 'mutex_id': var_mid} # armazena as variáveis dinâmicas

            ttk.Label(self.dynamic_frame, text="Instante inicial:").pack(anchor='w') # label instante
            ttk.Entry(self.dynamic_frame, textvariable=var_ing).pack(fill='x', pady=5) # entrada instante
            label_text = f"ID do Mutex (ex: M1, M2):" # label mutex
            ttk.Label(self.dynamic_frame, text=label_text).pack(anchor='w') # empacota o label
            ttk.Entry(self.dynamic_frame, textvariable=var_mid).pack(fill='x', pady=5) # entrada mutex id

        elif tipo in ["Envio", "Recebimento"]: # tipo Envio/Recebimento de Dados
            var_ing = tk.IntVar(value=defaults.get('instante', 0)) # instante padrão
            self.dynamic_vars = {'instante': var_ing} # armazena as variáveis dinâmicas
            ttk.Label(self.dynamic_frame, text="Instante inicial:").pack(anchor='w') # label instante
            ttk.Entry(self.dynamic_frame, textvariable=var_ing).pack(fill='x', pady=5) # entrada instante

        else: # tipo desconhecido ou nenhum
            if not tipo:
                ttk.Label(self.dynamic_frame, text="Selecione um tipo de evento acima.").pack() # instrução para selecionar tipo

    def _on_salvar(self):
        """Valida e salva os dados do evento."""
        # Chama a função de validação dos dados da tarefa
        valido, dados_ou_erro = self._validar_e_coletar_dados()
        
        if not valido:
            # Se falhar, mostra o erro e não fecha
            messagebox.showerror("Erro de Validação", dados_ou_erro, parent=self)
            return

        # Se for válido, 'dados_ou_erro' contém os dados prontos
        self.resultado = dados_ou_erro # armazena o resultado
        self.destroy() # fecha o modal

    def _validar_e_coletar_dados(self):
        """
        Função única que valida tudo.
        Retorna (True, dados) em sucesso.
        Retorna (False, "mensagem de erro") em falha.
        """
        try:
            tipo_evento_display = self.tipo_var.get() # obtém o tipo selecionado
            if not tipo_evento_display: # tipo vazio
                return (False, "Tipo do evento não pode ser vazio")

            # Coleta os dados brutos das variáveis dinâmicas
            dados_brutos = {}
            for nome_var, var_obj in self.dynamic_vars.items(): # itera sobre as variáveis dinâmicas
                dados_brutos[nome_var] = var_obj.get() # obtém o valor da variável

            # --- Validações ---
            instante = dados_brutos.get('instante') # obtém o instante
            if instante is not None and instante < 0: # verifica se o instante é negativo
                return (False, "O 'Instante inicial' não pode ser negativo.")

            if tipo_evento_display == "I/O": # validações específicas para I/O
                if dados_brutos.get('duracao', 0) <= 0: # verica se a duração é menor ou igual à 0
                    return (False, "A 'Duração do I/O' deve ser maior que 0.")
            
            if tipo_evento_display in ["Mutex Lock", "Mutex Unlock"]: # validações para Mutexes Locks e Unlocks
                if not dados_brutos.get('mutex_id', '').strip(): # verifica se tem um id
                    return (False, "O 'ID do Mutex' não pode ser vazio.")
            # --- Fim Validações ---
            # Mapeamento do tipo para abreviação
            mapa_tipos = {
                "I/O": "IO",
                "Mutex Lock": "ML",
                "Mutex Unlock": "MU",
                "Envio": "SND",
                "Recebimento": "RCV"
            } # mapeia nomes completos para abreviações

            # Mapeia o tipo
            tipo_evento_abrev = mapa_tipos.get(tipo_evento_display)

            # Constrói o resultado
            resultado_final = { "tipo_evento": tipo_evento_abrev } # inicia o resultado com o tipo
            resultado_final.update(dados_brutos) # Adiciona todos os dados dinâmicos

            return (True, resultado_final) # retorna sucesso com os dados
        
        except tk.TclError as e:
            return (False, f"Dado inválido: {e}\nCertifique-se que os campos são números.") # trata erros de conversão
        except Exception as e:
            return (False, f"Ocorreu um erro ao salvar o evento: {e}") # trata outros erros genéricos
        
    def _on_cancelar(self):
        """Cancela a operação e fecha o modal."""
        self.resultado = None # nenhum resultado
        self.destroy() # fecha o modal