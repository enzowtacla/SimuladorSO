# --- Makefile para Simulador com Nuitka (Tkinter + Matplotlib) ---

# O seu script Python principal (ex: main.py, app.py)
MAIN_SCRIPT = main.py

# O nome do executável de saída
TARGET_EXEC = simulador_SO

# O comando do compilador Nuitka
COMPILER = python3 -m nuitka

NUITKA_FLAGS_FINAL = --onefile --standalone --enable-plugin=tk-inter --enable-plugin=matplotlib
NUITKA_FLAGS_TEST = --standalone --enable-plugin=tk-inter --enable-plugin=matplotlib

# Alvo padrão (make)
all: compile

# Alvo de compilação FINAL (lento)
# Roda este comando para a sua entrega final
compile:
	@echo "--- Compilando [FINAL] com Nuitka (Tkinter + Matplotlib) ---"
	$(COMPILER) $(NUITKA_FLAGS_FINAL) $(MAIN_SCRIPT) -o $(TARGET_EXEC)
	@echo "--- Compilação final concluída: ./"$(TARGET_EXEC)" ---"

# Alvo de compilação de TESTE (rápido)
# Use 'make test-build' enquanto estiver desenvolvendo
test-build:
	@echo "--- Compilando [TESTE] com Nuitka (Tkinter + Matplotlib) ---"
	$(COMPILER) $(NUITKA_FLAGS_TEST) $(MAIN_SCRIPT) -o $(TARGET_EXEC)
	@echo "--- Build de teste concluído. O executável está em: $(TARGET_EXEC).dist/$(MAIN_SCRIPT_NAME) ---"

# Alvo para limpar os arquivos gerados
clean:
	@echo "--- Limpando arquivos de build ---"
	rm -rf *.build *.dist *.onefile-build
	rm -f $(TARGET_EXEC) $(TARGET_EXEC).exe
	@echo "--- Limpeza concluída ---"

make_run:
	@echo "--- Executando o simulador ---"
	./$(TARGET_EXEC)
	@echo "--- Execução concluída ---"

make_run_interpreted:
	@echo "--- Executando o simulador no interpretador Python ---"
	python3 $(MAIN_SCRIPT)
	@echo "--- Execução concluída ---"