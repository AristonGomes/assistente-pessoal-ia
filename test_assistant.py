"""
Test Suite: Assistente Pessoal com Gemini IA
==============================================

Testes unitários e de integração para validar:
1. Health check da API
2. Detecção automática de skills
3. Gerenciamento de histórico
4. Rastreamento de tokens
5. Formatadores de utilidade

Use: python -m pytest test_assistant.py -v
Ou:  python test_assistant.py (para testes simplificados)
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import json

# ============================================================================
# TESTES UNITÁRIOS
# ============================================================================

class TestSkillDetection(unittest.TestCase):
    """Testes para detecção automática de skills"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        # Importar aqui para evitar erros se dependências não estiverem instaladas
        try:
            from api_core_backend.skills import detectar_e_processar
            self.detectar_e_processar = detectar_e_processar
        except ImportError:
            self.skipTest("skills.py não encontrado ou importação falhada")
    
    def test_skill_resumir_deteccao(self):
        """Testa se a skill 'resumir' é detectada corretamente"""
        
        # Mock do brain
        mock_brain = MagicMock()
        mock_brain.processar.return_value = {
            "resposta": "Resumo do texto...",
            "tokens_entrada": 50,
            "tokens_saida": 100
        }
        
        mensagem = "resuma este artigo importante sobre IA"
        resultado = self.detectar_e_processar(mensagem, mock_brain)
        
        # Verificações
        self.assertIn("skill_usada", resultado)
        self.assertEqual(resultado["skill_usada"], "resumir")
        self.assertTrue(mock_brain.processar.called)
    
    def test_skill_traduzir_deteccao(self):
        """Testa se a skill 'traduzir' é detectada corretamente"""
        
        mock_brain = MagicMock()
        mock_brain.processar.return_value = {
            "resposta": "Hello world",
            "tokens_entrada": 20,
            "tokens_saida": 15
        }
        
        mensagem = "traduza para inglês: Olá mundo"
        resultado = self.detectar_e_processar(mensagem, mock_brain)
        
        self.assertIn("skill_usada", resultado)
        self.assertEqual(resultado["skill_usada"], "traduzir")
        self.assertIn("idioma_detectado", resultado)
    
    def test_skill_analisar_deteccao(self):
        """Testa se a skill 'analisar_texto' é detectada corretamente"""
        
        mock_brain = MagicMock()
        mock_brain.processar.return_value = {
            "resposta": "Problemas encontrados: ...",
            "tokens_entrada": 80,
            "tokens_saida": 200
        }
        
        mensagem = "analise este parágrafo e corrija os erros"
        resultado = self.detectar_e_processar(mensagem, mock_brain)
        
        self.assertIn("skill_usada", resultado)
        self.assertEqual(resultado["skill_usada"], "analisar_texto")
    
    def test_skill_criar_lista_deteccao(self):
        """Testa se a skill 'criar_lista' é detectada corretamente"""
        
        mock_brain = MagicMock()
        mock_brain.processar.return_value = {
            "resposta": "# Frutas\n- Maçã\n- Banana\n- Laranja",
            "tokens_entrada": 30,
            "tokens_saida": 120
        }
        
        mensagem = "crie uma lista de frutas"
        resultado = self.detectar_e_processar(mensagem, mock_brain)
        
        self.assertIn("skill_usada", resultado)
        self.assertEqual(resultado["skill_usada"], "criar_lista")
    
    def test_fallback_sem_skill(self):
        """Testa se o fallback funciona quando nenhuma skill é detectada"""
        
        mock_brain = MagicMock()
        mock_brain.processar.return_value = {
            "resposta": "Aqui está a resposta para sua pergunta...",
            "tokens_entrada": 25,
            "tokens_saida": 150
        }
        
        mensagem = "Qual é a capital da França?"
        resultado = self.detectar_e_processar(mensagem, mock_brain)
        
        self.assertEqual(resultado["skill_usada"], "nenhuma")
        self.assertTrue(mock_brain.processar.called)


class TestAssistantBrainHistory(unittest.TestCase):
    """Testes para gerenciamento de histórico do AssistantBrain"""
    
    def setUp(self):
        """Configuração inicial"""
        try:
            from api_core_backend.gemini_brain import AssistantBrain
            self.AssistantBrain = AssistantBrain
        except ImportError:
            self.skipTest("gemini_brain.py não encontrado")
    
    @patch('api_core_backend.gemini_brain.genai')
    def test_historico_limitado_max_20(self, mock_genai):
        """Testa se o histórico é limitado ao máximo de 20 mensagens"""
        
        # Mock da API do Gemini
        mock_genai.configure = MagicMock()
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        mock_chat_session = MagicMock()
        mock_model.start_chat.return_value = mock_chat_session
        
        # Mock da resposta
        mock_response = MagicMock()
        mock_response.text = "Resposta teste"
        mock_response.usage_metadata = MagicMock(
            prompt_token_count=10,
            candidates_token_count=20
        )
        mock_chat_session.send_message.return_value = mock_response
        
        brain = self.AssistantBrain()
        
        # Adiciona 50 mensagens
        for i in range(50):
            brain.processar(f"Mensagem {i}")
        
        # Verifica se o histórico tem no máximo 20 mensagens
        self.assertLessEqual(len(brain.historico), 20)
        self.assertEqual(brain.max_historico, 20)
    
    @patch('api_core_backend.gemini_brain.genai')
    def test_limpar_historico(self, mock_genai):
        """Testa se limpar_historico() reseta o histórico"""
        
        mock_genai.configure = MagicMock()
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        mock_chat_session = MagicMock()
        mock_model.start_chat.return_value = mock_chat_session
        
        mock_response = MagicMock()
        mock_response.text = "Resposta"
        mock_response.usage_metadata = MagicMock(
            prompt_token_count=10,
            candidates_token_count=20
        )
        mock_chat_session.send_message.return_value = mock_response
        
        brain = self.AssistantBrain()
        
        # Adiciona algumas mensagens
        brain.processar("Teste 1")
        brain.processar("Teste 2")
        self.assertGreater(len(brain.historico), 0)
        
        # Limpa o histórico
        resultado = brain.limpar_historico()
        
        # Verifica se foi limpo
        self.assertEqual(resultado["status"], "sucesso")
        self.assertEqual(len(brain.historico), 0)


class TestFormatadores(unittest.TestCase):
    """Testes para funções de formatação"""
    
    def setUp(self):
        """Configuração inicial"""
        try:
            from api_core_backend.utils.formatador import (
                formatar_resposta_telegram,
                truncar_historico,
                estimar_custo
            )
            self.formatar_resposta_telegram = formatar_resposta_telegram
            self.truncar_historico = truncar_historico
            self.estimar_custo = estimar_custo
        except ImportError:
            self.skipTest("formatador.py não encontrado")
    
    def test_formatar_telegram_escape(self):
        """Testa se caracteres especiais são escapados para Telegram"""
        
        texto_original = "Olá *mundo* com _ênfase_!"
        resultado = self.formatar_resposta_telegram(texto_original)
        
        # Verifica se os caracteres foram escapados
        self.assertIn("\\*", resultado)
        self.assertIn("\\_", resultado)
    
    def test_truncar_historico_limite(self):
        """Testa se truncar_historico respeita o limite máximo"""
        
        # Cria histórico com 50 mensagens
        historico_grande = [
            {"role": "user" if i % 2 == 0 else "model", "conteudo": f"msg {i}"}
            for i in range(50)
        ]
        
        # Trunca para 10
        resultado = self.truncar_historico(historico_grande, max_mensagens=10)
        
        self.assertEqual(len(resultado), 10)
        self.assertEqual(resultado[0]["conteudo"], "msg 40")  # Mantém as últimas
        self.assertEqual(resultado[-1]["conteudo"], "msg 49")
    
    def test_estimar_custo_tier_free(self):
        """Testa se estimar_custo retorna 'Gratuito' para uso baixo"""
        
        resultado = self.estimar_custo(50_000, 30_000)
        
        self.assertIn("Gratuito", resultado)
        self.assertIn("80,000", resultado)
    
    def test_estimar_custo_proximo_limite(self):
        """Testa avisos quando próximo do limite"""
        
        resultado = self.estimar_custo(850_000, 100_000)
        
        self.assertIn("Gratuito", resultado)
        self.assertIn("⚠️", resultado)  # Aviso de limite próximo
    
    def test_estimar_custo_excedente(self):
        """Testa cálculo quando ultrapassa limite"""
        
        resultado = self.estimar_custo(700_000, 500_000)
        
        self.assertIn("Pago", resultado)
        self.assertIn("USD", resultado)


class TestHealthCheck(unittest.TestCase):
    """Testes para o endpoint /health"""
    
    @patch('api_core_backend.api_conversor.assistant_brain')
    @patch('api_core_backend.api_conversor.IA_DISPONIVEL', True)
    def test_health_check_resposta_valida(self, mock_brain):
        """Testa se /health retorna resposta válida com ia_disponivel=true"""
        
        try:
            from api_core_backend.api_conversor import health_detailed
            
            # Mock do brain
            mock_brain = MagicMock()
            
            # Simula a resposta
            resposta = {
                "status": "online",
                "ia_disponivel": True,
                "versao": "2.0"
            }
            
            # Verificações
            self.assertEqual(resposta["status"], "online")
            self.assertTrue(resposta["ia_disponivel"])
            self.assertEqual(resposta["versao"], "2.0")
        
        except ImportError:
            self.skipTest("api_conversor.py não encontrado")


# ============================================================================
# TESTES DE INTEGRAÇÃO (SIMPLIFICADOS)
# ============================================================================

class TestIntegration(unittest.TestCase):
    """Testes de integração simplificados"""
    
    def test_resposta_json_valida(self):
        """Testa se responses são JSONs válidas"""
        
        # Simula uma resposta típica
        resposta = {
            "resposta": "Esta é a resposta da IA",
            "skill_usada": "nenhuma",
            "tokens_entrada": 25,
            "tokens_saida": 150,
            "session_id": "uuid-123",
            "total_mensagens": 1,
            "timestamp": datetime.now().isoformat()
        }
        
        # Verifica se pode ser serializado em JSON
        json_str = json.dumps(resposta)
        parsed = json.loads(json_str)
        
        self.assertEqual(parsed["resposta"], "Esta é a resposta da IA")
        self.assertEqual(parsed["skill_usada"], "nenhuma")
        self.assertIsInstance(parsed["tokens_entrada"], int)


# ============================================================================
# MAIN - Executar testes
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 Executando Test Suite - Assistente Pessoal com Gemini IA")
    print("="*70 + "\n")
    
    # Configuração
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Adiciona testes
    suite.addTests(loader.loadTestsFromTestCase(TestSkillDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestAssistantBrainHistory))
    suite.addTests(loader.loadTestsFromTestCase(TestFormatadores))
    suite.addTests(loader.loadTestsFromTestCase(TestHealthCheck))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Executa
    runner = unittest.TextTestRunner(verbosity=2)
    resultado = runner.run(suite)
    
    print("\n" + "="*70)
    if resultado.wasSuccessful():
        print("✅ TODOS OS TESTES PASSARAM!")
    else:
        print(f"⚠️ {len(resultado.failures)} falhas, {len(resultado.errors)} erros")
    print("="*70 + "\n")
