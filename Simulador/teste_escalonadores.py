import unittest
from Simulador.tarefa import Tarefa, Evento
from Simulador.escalonadorFIFO import EscalonadorFIFO
from Simulador.escalonadorPrioP import EscalonadorPRIOP
from Simulador.escalonadorSRTF import EscalonadorSRTF


class TestEscalonadores(unittest.TestCase):
    
    def setUp(self):
        """Configura tarefas de teste para usar nos testes."""
        # Tarefas com diferentes características para testar os escalonadores
        self.tarefa1 = Tarefa(
            id="T1", cor=1, ingresso=0, duracao=10, prioridade=3, eventos=[]
        )
        self.tarefa2 = Tarefa(
            id="T2", cor=2, ingresso=1, duracao=5, prioridade=1, eventos=[]
        )
        self.tarefa3 = Tarefa(
            id="T3", cor=3, ingresso=2, duracao=8, prioridade=2, eventos=[]
        )
        
        # Simula execução parcial das tarefas para teste do SRTF
        self.tarefa1_parcial = Tarefa(
            id="T1", cor=1, ingresso=0, duracao=10, prioridade=3, eventos=[]
        )
        self.tarefa1_parcial.executar(3)  # Executa 3 unidades, restam 7
        
        self.tarefa2_parcial = Tarefa(
            id="T2", cor=2, ingresso=1, duracao=5, prioridade=1, eventos=[]
        )
        self.tarefa2_parcial.executar(1)  # Executa 1 unidade, restam 4
        
        self.tarefa3_parcial = Tarefa(
            id="T3", cor=3, ingresso=2, duracao=8, prioridade=2, eventos=[]
        )
        self.tarefa3_parcial.executar(2)  # Executa 2 unidades, restam 6

    def test_escalonador_fifo_ordem_correta(self):
        """Testa se o escalonador FIFO retorna tarefas na ordem FIFO."""
        tarefas = [self.tarefa1, self.tarefa2, self.tarefa3]
        escalonador = EscalonadorFIFO(tarefas)
        
        # Primeira tarefa deve ser T1 (primeira da fila)
        primeira = escalonador.escalonar()
        self.assertEqual(primeira.id, "T1")
        
        # Segunda tarefa deve ser T2
        segunda = escalonador.escalonar()
        self.assertEqual(segunda.id, "T2")
        
        # Terceira tarefa deve ser T3
        terceira = escalonador.escalonar()
        self.assertEqual(terceira.id, "T3")

    def test_escalonador_fifo_lista_vazia(self):
        """Testa comportamento do FIFO com lista vazia."""
        escalonador = EscalonadorFIFO([])
        resultado = escalonador.escalonar()
        self.assertIsNone(resultado)

    def test_escalonador_fifo_tarefas_none(self):
        """Testa comportamento do FIFO com tarefas None."""
        escalonador = EscalonadorFIFO(None)
        resultado = escalonador.escalonar()
        self.assertIsNone(resultado)

    def test_escalonador_priop_maior_prioridade(self):
        """Testa se o escalonador de prioridade retorna a tarefa com maior prioridade."""
        tarefas = [self.tarefa1, self.tarefa2, self.tarefa3]
        escalonador = EscalonadorPRIOP(tarefas.copy())
        
        # Deve retornar T1 (prioridade 3 - maior número = maior prioridade)
        resultado = escalonador.escalonar()
        self.assertEqual(resultado.id, "T1")
        self.assertEqual(resultado.prioridade, 3)

    def test_escalonador_priop_ordenacao_prioridades(self):
        """Testa a ordenação completa por prioridades."""
        # T1(prio=3), T2(prio=1), T3(prio=2) - ordem esperada: T1, T3, T2
        
        # Teste 1: Todas as tarefas - deve retornar T1 (prioridade 3)
        escalonador1 = EscalonadorPRIOP([self.tarefa1, self.tarefa2, self.tarefa3])
        primeira = escalonador1.escalonar()
        self.assertEqual(primeira.id, "T1")
        
        # Teste 2: Sem T1 - deve retornar T3 (prioridade 2)
        escalonador2 = EscalonadorPRIOP([self.tarefa2, self.tarefa3])
        segunda = escalonador2.escalonar()
        self.assertEqual(segunda.id, "T3")
        
        # Teste 3: Só T2 - deve retornar T2 (prioridade 1)
        escalonador3 = EscalonadorPRIOP([self.tarefa2])
        terceira = escalonador3.escalonar()
        self.assertEqual(terceira.id, "T2")

    def test_escalonador_priop_tarefas_none(self):
        """Testa comportamento do PrioP com tarefas None."""
        escalonador = EscalonadorPRIOP(None)
        resultado = escalonador.escalonar()
        self.assertIsNone(resultado)

    def test_escalonador_srtf_menor_tempo_restante(self):
        """Testa se o SRTF retorna a tarefa com menor tempo restante."""
        tarefas = [self.tarefa1_parcial, self.tarefa2_parcial, self.tarefa3_parcial]
        escalonador = EscalonadorSRTF(tarefas.copy())
        
        # Deve retornar T2 (tempo restante = 4)
        resultado = escalonador.escalonar()
        self.assertEqual(resultado.id, "T2")
        self.assertEqual(resultado.t_restante, 4)

    def test_escalonador_srtf_ordenacao_tempo_restante(self):
        """Testa a ordenação completa por tempo restante."""
        tarefas = [self.tarefa1_parcial, self.tarefa2_parcial, self.tarefa3_parcial]
        escalonador = EscalonadorSRTF(tarefas.copy())
        
        # Primeira execução - T2 (tempo restante = 4)
        primeira = escalonador.escalonar()
        self.assertEqual(primeira.id, "T2")
        self.assertEqual(primeira.t_restante, 4)
        
        # Remove T2 e testa novamente
        escalonador.tarefas.remove(primeira)
        segunda = escalonador.escalonar()
        self.assertEqual(segunda.id, "T3")  # tempo restante = 6
        
        # Remove T3 e testa novamente
        escalonador.tarefas.remove(segunda)
        terceira = escalonador.escalonar()
        self.assertEqual(terceira.id, "T1")  # tempo restante = 7

    def test_escalonador_srtf_tarefas_novas(self):
        """Testa SRTF com tarefas não executadas (tempo restante = duração)."""
        tarefas = [self.tarefa1, self.tarefa2, self.tarefa3]
        escalonador = EscalonadorSRTF(tarefas.copy())
        
        # Deve retornar T2 (menor duração = 5)
        resultado = escalonador.escalonar()
        self.assertEqual(resultado.id, "T2")
        self.assertEqual(resultado.t_restante, 5)

    def test_escalonador_srtf_tarefas_none(self):
        """Testa comportamento do SRTF com tarefas None."""
        escalonador = EscalonadorSRTF(None)
        resultado = escalonador.escalonar()
        self.assertIsNone(resultado)

    def test_cenario_completo_comparacao(self):
        """Testa um cenário completo comparando os três escalonadores."""
        # Mesmo conjunto de tarefas para todos os escalonadores
        tarefas_base = [
            Tarefa(id="A", cor=1, ingresso=0, duracao=6, prioridade=2, eventos=[]),
            Tarefa(id="B", cor=2, ingresso=1, duracao=3, prioridade=1, eventos=[]),
            Tarefa(id="C", cor=3, ingresso=2, duracao=4, prioridade=3, eventos=[])
        ]
        
        # FIFO: deve retornar A (primeira da fila)
        fifo = EscalonadorFIFO(tarefas_base.copy())
        resultado_fifo = fifo.escalonar()
        self.assertEqual(resultado_fifo.id, "A")
        
        # PrioP: deve retornar C (prioridade 3 - maior número = maior prioridade)
        priop = EscalonadorPRIOP(tarefas_base.copy())
        resultado_priop = priop.escalonar()
        self.assertEqual(resultado_priop.id, "C")
        
        # SRTF: deve retornar B (menor duração = 3)
        srtf = EscalonadorSRTF(tarefas_base.copy())
        resultado_srtf = srtf.escalonar()
        self.assertEqual(resultado_srtf.id, "B")

    def test_execucao_tarefa_e_tempo_restante(self):
        """Testa se a execução de tarefas afeta corretamente o tempo restante."""
        tarefa = Tarefa(id="TEST", cor=1, ingresso=0, duracao=10, prioridade=1, eventos=[])
        
        # Inicialmente tempo restante deve ser igual à duração
        self.assertEqual(tarefa.t_restante, 10)
        self.assertEqual(tarefa.t_executado, 0)
        
        # Executa por 3 unidades
        tempo_executado = tarefa.executar(3)
        self.assertEqual(tempo_executado, 3)
        self.assertEqual(tarefa.t_restante, 7)
        self.assertEqual(tarefa.t_executado, 3)
        
        # Executa por mais 5 unidades
        tempo_executado = tarefa.executar(5)
        self.assertEqual(tempo_executado, 5)
        self.assertEqual(tarefa.t_restante, 2)
        self.assertEqual(tarefa.t_executado, 8)
        
        # Tenta executar por 5 unidades, mas só restam 2
        tempo_executado = tarefa.executar(5)
        self.assertEqual(tempo_executado, 2)
        self.assertEqual(tarefa.t_restante, 0)
        self.assertEqual(tarefa.t_executado, 10)
        self.assertTrue(tarefa.finalizada)


if __name__ == "__main__":
    unittest.main()
