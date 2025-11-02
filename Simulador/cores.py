# Lista de cores para o Gantt. O arquivo de config usa 'cor' como índice.
CORES_TAREFAS = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#00FFFF", "#FF00FF",
                "#800000", "#008000", "#000080", "#808000", "#008080", "#800080",
                "#C0C0C0", "#FF6347", "#ADFF2F", "#1E90FF", "#FFD700", "#40E0D0"]

COR_TAREFA_NAO_EXECUTANDO = "#A9A9A9"  # Cinza escuro para tarefas não executando
NOMES_CORES = [
    "Vermelho", "Verde", "Azul", "Amarelo", "Ciano", "Magenta",
    "Marrom", "Verde Escuro", "Azul Marinho", "Oliva", "Teal", "Roxo",
    "Prata", "Tomate", "Verde Lima", "Azul Céu", "Dourado", "Turquesa"
]

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

def get_lista_cores_para_combobox():
    """Retorna lista formatada para combobox"""
    lista = []
    for i in range(len(CORES_TAREFAS)):
        nome = get_cor_nome(i)
        lista.append(f"{i}: {nome}")
    return lista

def extrair_id_cor_do_texto(texto_combobox):
    """Extrai o ID da cor do texto do combobox"""
    return int(texto_combobox.split(':')[0])