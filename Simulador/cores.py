# Lista de cores para o Gantt. O arquivo de config usa 'cor' como índice.
CORES_TAREFAS = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#00FFFF", "#FF00FF",
                "#800000", "#008000", "#000080", "#808000", "#008080", "#800080",
                "#C0C0C0", "#FF6347", "#ADFF2F", "#1E90FF", "#FFD700", "#40E0D0"]

COR_TAREFA_NAO_EXECUTANDO = "#A9A9A9"  # Cinza escuro para tarefas não executando

# nome das cores correspondentes aos índices -  utilizado na configuração manual
NOMES_CORES = [
    "Vermelho", "Verde", "Azul", "Amarelo", "Ciano", "Magenta",
    "Marrom", "Verde Escuro", "Azul Marinho", "Oliva", "Teal", "Roxo",
    "Prata", "Tomate", "Verde Lima", "Azul Céu", "Dourado", "Turquesa"
]

# Funções auxiliares para manipulação de cores

# pegar nome e hex da cor pelo id
def get_cor_nome(id_cor):
    """Retorna o nome da cor pelo ID"""
    if 0 <= id_cor < len(NOMES_CORES):
        return NOMES_CORES[id_cor]
    return f"Cor {id_cor}"

def get_cor_hex(id_cor):
    """Retorna o código hex da cor pelo ID"""
    if 0 <= id_cor < len(CORES_TAREFAS):
        return CORES_TAREFAS[id_cor]
    return "#808080" 

# lista de cores formatada para combobox - id: nome
def get_lista_cores_para_combobox():
    """Retorna lista formatada para combobox"""
    lista = []
    for i in range(len(CORES_TAREFAS)):
        nome = get_cor_nome(i)
        lista.append(f"{i}: {nome}")
    return lista

# Extrai o ID da cor do texto do combobox
def extrair_id_cor_do_texto(texto_combobox):
    """Extrai o ID da cor do texto do combobox"""
    return int(texto_combobox.split(':')[0])

def get_cor_by_hex(hex_code):
    """Retorna o ID da cor pelo código hex."""
    # Garante que tenha o #
    if not hex_code.startswith('#'):
        hex_code = '#' + hex_code
    
    # Procura na lista de cores
    for i, cor in enumerate(CORES_TAREFAS):
        if cor.lower() == hex_code.lower():
            return i
    
    # Se não encontrar, tenta encontrar a cor mais próxima
    # Para simplificar, retorna 0 (vermelho) como fallback
    return 0