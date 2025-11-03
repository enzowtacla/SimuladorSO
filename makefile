# --- Makefile v4.1 (FINAL - Corrige .spec E o bug do PIL/Matplotlib) ---

# --- Configuração ---
VENV_NAME = venv
MAIN_SCRIPT = main.py
TARGET_EXEC = top_simulador
SPEC_FILE = $(TARGET_EXEC).spec

# --- Comandos do VENV ---
PYTHON = $(VENV_NAME)/bin/python3
PIP = $(VENV_NAME)/bin/pip
PACKAGER = $(VENV_NAME)/bin/pyinstaller

# --- Flags para GERAÇÃO do .spec (Com a correção do PIL) ---
PYINSTALLER_FLAGS_GEN = --onedir --windowed --name=$(TARGET_EXEC) \
                        --collect-all matplotlib \
                        --collect-all mpl_toolkits \
                        --hidden-import=PIL._tkinter_finder

# --- Caminhos ---
FINAL_EXEC_PATH = dist/$(TARGET_EXEC)/$(TARGET_EXEC)

# --- Alvos Principais ---
all: compile

# Cria o ambiente virtual
$(VENV_NAME):
	@echo "--- Criando ambiente virtual limpo em [$(VENV_NAME)] ---"
	python3 -m venv $(VENV_NAME)

# Instala dependências DENTRO do venv
install-build-deps: $(VENV_NAME)
	@echo "--- Instalando dependências DENTRO do venv ---"
	$(PIP) install --upgrade pip wheel
	$(PIP) install --force-reinstall pyinstaller "matplotlib==3.7.5"
	@echo "--- Dependências de build (isoladas) instaladas ---"

# 1. Gera o arquivo .spec (que estará quebrado)
# O '-' ignora o erro e o '|| true' garante que o make continue
generate-spec: install-build-deps
	@echo "--- 1. Gerando arquivo .spec (pode estar quebrado) ---"
	-$(PACKAGER) --specpath . $(PYINSTALLER_FLAGS_GEN) $(MAIN_SCRIPT) || true
	@test -f $(SPEC_FILE) || (echo "❌ Falha ao gerar o .spec!" && exit 1)
	@echo "--- .spec gerado ---"

# 2. Edita o .spec para remover a linha quebrada
patch-spec: generate-spec
	@echo "--- 2. Removendo referências ao lixo 'SimuladorSO' do .spec ---"
	sed -i "/SimuladorSO/d" $(SPEC_FILE)
	@echo "--- .spec corrigido ---"

# 3. Compila usando o .spec CORRIGIDO
compile: patch-spec
	@echo "--- 3. Compilando usando o .spec corrigido ---"
	$(PACKAGER) --clean $(SPEC_FILE)
	@echo "--- ✅ Empacotamento final concluído: $(FINAL_EXEC_PATH) ---"

# Executa o executável final
run:
	@echo "--- Executando simulador standalone (da pasta dist/) ---"
	@test -f $(FINAL_EXEC_PATH) || (echo "❌ Executável não encontrado! Execute 'make compile' primeiro." && exit 1)
	./$(FINAL_EXEC_PATH)
	@echo "--- Execução concluída ---"

# Executa no modo de desenvolvimento (usando o venv)
run-dev: install-build-deps
	@echo "--- Executando no interpretador Python (dentro do venv) ---"
	$(PYTHON) $(MAIN_SCRIPT)

# Limpa TUDO, incluindo o venv
clean:
	@echo "--- Limpando TUDO (build, dist, spec, venv, execs) ---"
	rm -rf build/ dist/ __pycache__/ *.spec $(VENV_NAME)
	rm -f $(TARGET_EXEC) $(TARGET_EXEC).exe
	@echo "--- Limpeza concluída ---"

# Help
help:
	@echo "=== Simulador SO - Build com VENV (Solução de Patch) ==="
	@echo ""
	@echo "🔧 PARA EMPACOTAR:"
	@echo "  make compile    - Gera, corrige e compila o .spec (solução completa)"
	@echo ""
	@echo "🚀 PARA EXECUTAR:"
	@echo "  make run        - Executa o app empacotado"
	@echo ""
	@echo "🛠️  DESENVOLVIMENTO:"
	@echo "  make run-dev    - Executa no Python (isolado no venv)"
	@echo "  make clean      - Remove TUDO (dist, build, e o venv)"

.PHONY: all compile run run-dev clean install-build-deps generate-spec patch-spec help