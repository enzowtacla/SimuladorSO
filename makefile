# --- Makefile para Simulador com Nuitka (Tkinter + Matplotlib) ---

# O seu script Python principal (ex: main.py, app.py)
MAIN_SCRIPT = main.py
MAIN_SCRIPT_NAME = main

# O nome do executável de saída
TARGET_EXEC = simulador_SO

# O comando do compilador Nuitka
COMPILER = python3 -m nuitka

NUITKA_FLAGS_FINAL = --onefile --standalone --enable-plugin=tk-inter --enable-plugin=matplotlib
NUITKA_FLAGS_TEST = --standalone --enable-plugin=tk-inter --enable-plugin=matplotlib

# Alvo padrão (make)
all: compile

# Verifica se Python está instalado (NECESSÁRIO para compilação)
check-python:
	@echo "--- Verificando Python (NECESSÁRIO para compilação) ---"
	@which python3 >/dev/null 2>&1 || (echo "❌ Python 3 é OBRIGATÓRIO para compilar com Nuitka!" && echo "📦 Instale com: sudo apt-get install python3 python3-pip python3-tk" && exit 1)
	@python3 --version
	@echo "✅ Python 3 OK (necessário para build)"

# Instala dependências de BUILD
install-build-deps: check-python
	@echo "--- Instalando dependências para COMPILAÇÃO ---"
	pip3 install --user nuitka matplotlib
	@echo "--- Dependências de build instaladas ---"

# Verifica tkinter (necessário para compilação)
check-tkinter: check-python
	@echo "--- Verificando tkinter ---"
	@python3 -c "import tkinter; print('✅ tkinter OK')" || (echo "❌ tkinter necessário para build. Instale: sudo apt-get install python3-tk" && exit 1)

# Alvo de compilação FINAL (lento)
compile: check-python check-tkinter install-build-deps
	@echo "--- Compilando [FINAL] com Nuitka ---"
	@echo "ℹ️  Python é necessário APENAS para compilação"
	@echo "🚀 O executável final NÃO precisará de Python!"
	$(COMPILER) $(NUITKA_FLAGS_FINAL) $(MAIN_SCRIPT) -o $(TARGET_EXEC)
	@echo "--- ✅ Compilação final concluída: ./"$(TARGET_EXEC)" ---"
	@echo "🎯 Este executável pode rodar em qualquer máquina Linux (sem Python)!"

# Alvo de compilação de TESTE (rápido)
test-build: check-python check-tkinter install-build-deps
	@echo "--- Compilando [TESTE] com Nuitka ---"
	$(COMPILER) $(NUITKA_FLAGS_TEST) $(MAIN_SCRIPT) -o $(TARGET_EXEC)
	@echo "--- Build de teste concluído ---"

# Executa o executável (NÃO precisa de Python)
run:
	@echo "--- Executando simulador standalone ---"
	@test -f $(TARGET_EXEC) || (echo "❌ Executável não encontrado! Execute 'make compile' primeiro." && exit 1)
	@echo "ℹ️  Este executável NÃO precisa de Python instalado!"
	./$(TARGET_EXEC)
	@echo "--- Execução concluída ---"

# Executa no Python (para desenvolvimento)
run-dev: check-python
	@echo "--- Executando no interpretador Python ---"
	python3 $(MAIN_SCRIPT)

# Limpa arquivos de build
clean:
	@echo "--- Limpando arquivos de build ---"
	rm -rf *.build *.dist *.onefile-build
	rm -f $(TARGET_EXEC) $(TARGET_EXEC).exe
	@echo "--- Limpeza concluída ---"

# Instala Python (Ubuntu/Debian) - NECESSÁRIO para compilação
install-python-ubuntu:
	@echo "--- Instalando Python 3 (NECESSÁRIO para build) ---"
	sudo apt-get update
	sudo apt-get install -y python3 python3-pip python3-tk python3-dev
	@echo "--- Python 3 instalado (agora você pode compilar) ---"

# Help
help:
	@echo "=== Simulador SO - Build com Nuitka ==="
	@echo ""
	@echo "🔧 PARA COMPILAR (precisa Python):"
	@echo "  make compile          - Compila executável standalone"
	@echo "  make test-build       - Build de teste"
	@echo ""
	@echo "🚀 PARA EXECUTAR (NÃO precisa Python):"
	@echo "  make run              - Executa o executável compilado"
	@echo ""
	@echo "🛠️  DESENVOLVIMENTO:"
	@echo "  make run-dev          - Executa no Python (desenvolvimento)"
	@echo "  make clean            - Remove arquivos de build"
	@echo ""
	@echo "📦 INSTALAÇÃO (se Python não estiver instalado):"
	@echo "  make install-python-ubuntu  - Instala Python no Ubuntu"
	@echo ""
	@echo "📋 FLUXO COMPLETO:"
	@echo "  1. Instalar Python (só na máquina de desenvolvimento)"
	@echo "  2. make compile (gera executável standalone)"
	@echo "  3. make run (executa - funciona sem Python!)"

.PHONY: all compile test-build run run-dev clean check-python install-build-deps check-tkinter install-python-ubuntu help