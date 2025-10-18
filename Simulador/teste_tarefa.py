#!/usr/bin/env python3
"""
Teste simples para a classe Tarefa
"""
from tarefa import Tarefa, Evento

def test_tarefa_basica():
    print("=== Teste 1: Criação de Tarefa ===")
    
    # Cria uma tarefa simples
    tarefa = Tarefa(
        id="T1",
        cor=1,
        ingresso=0,
        duracao=10,
        prioridade=1,
        eventos=[]
    )
    
    print(f"Tarefa {tarefa.id} criada:")
    print(f"  Estado: {tarefa.estado}")
    print(f"  Duração total: {tarefa.duracao}")
    print(f"  Tempo restante: {tarefa.t_restante}")
    print(f"  Está pronta? {tarefa.pronta}")
    print(f"  Está finalizada? {tarefa.finalizada}")
    print()

def test_execucao_tarefa():
    print("=== Teste 2: Execução da Tarefa ===")
    
    tarefa = Tarefa(
        id="T2", 
        cor=2,
        ingresso=0,
        duracao=8,
        prioridade=2,
        eventos=[]
    )
    
    print("Antes da execução:")
    print(f"  Tempo executado: {tarefa.t_executado}")
    print(f"  Tempo restante: {tarefa.t_restante}")
    
    # Executa a tarefa
    tempo_usado = tarefa.executar(quantum=3)
    print(f"\nExecutou por {tempo_usado} unidades:")
    print(f"  Tempo executado: {tarefa.t_executado}")
    print(f"  Tempo restante: {tarefa.t_restante}")
    print(f"  Estado: {tarefa.estado}")
    
    # Executa mais um pouco
    tempo_usado = tarefa.executar(quantum=4)
    print(f"\nExecutou por {tempo_usado} unidades:")
    print(f"  Tempo executado: {tarefa.t_executado}")
    print(f"  Tempo restante: {tarefa.t_restante}")
    
    # Executa até finalizar
    tempo_usado = tarefa.executar(quantum=10)  # Quantum maior que o restante
    print(f"\nExecutou por {tempo_usado} unidades (finalizando):")
    print(f"  Tempo executado: {tarefa.t_executado}")
    print(f"  Tempo restante: {tarefa.t_restante}")
    print(f"  Estado: {tarefa.estado}")
    print(f"  Está finalizada? {tarefa.finalizada}")
    print()

def test_tarefa_com_eventos():
    print("=== Teste 3: Tarefa com Eventos ===")
    
    # CORREÇÃO: Passe os valores ao criar o Evento
    evento_io = Evento(tipo="I/O", instante=3, duracao=2)
    evento_mutex = Evento(tipo="ML", instante=6, duracao=1)
    
    tarefa = Tarefa(
        id="T3",
        cor=3,
        ingresso=2,
        duracao=12,
        prioridade=1,
        eventos=[evento_io, evento_mutex]
    )
    
    print(f"Tarefa {tarefa.id} com {len(tarefa.eventos)} eventos:")
    for i, evento in enumerate(tarefa.eventos):
        print(f"  Evento {i+1}: {evento.tipo} no instante {evento.instante} (dura {evento.duracao})")

if __name__ == "__main__":
    test_tarefa_basica()
    test_execucao_tarefa()
    test_tarefa_com_eventos()
    print("✅ Todos os testes concluídos!")