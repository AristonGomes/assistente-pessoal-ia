"""
Módulo: Gemini Brain
=====================

Encapsula a integração com a Gemini API (Google GenerativeAI).
Responsável por gerenciar o histórico de conversa e processar mensagens
através do modelo gemini-1.5-flash.

O assistente é "Orion" - inteligente, prestativo e com toque de humor.
"""

import os
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv
import google.generativeai as genai

# Carrega variáveis de ambiente
load_dotenv()


class AssistantBrain:
    """
    Classe principal que representa o cérebro do assistente.
    
    Responsabilidades:
    - Inicializar e configurar o modelo Gemini
    - Manter histórico de conversa (máx. 20 mensagens)
    - Processar mensagens do usuário
    - Rastrear uso de tokens
    - Fornecer estatísticas da sessão
    """
    
    # Sistema de prompt do assistente Orion
    SYSTEM_INSTRUCTION = """Você é um assistente pessoal inteligente chamado Orion.
Você é direto, prestativo e levemente bem-humorado.
Você pode ajudar com:

• Responder perguntas gerais
• Resumir textos enviados pelo usuário
• Traduzir textos para qualquer idioma
• Analisar e limpar textos (melhor que regex!)
• Converter unidades e temperaturas
• Explicar conceitos de forma simples
• Criar listas, planos e estruturas

Responda sempre em português, de forma clara e objetiva."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa o AssistantBrain.
        
        Args:
            api_key (str, optional): Chave de API do Gemini. 
                                     Se não fornecida, tenta carregar de GEMINI_API_KEY.
        
        Raises:
            ValueError: Se a chave de API não for fornecida ou encontrada.
        """
        # Obtém a chave de API
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY não encontrada. "
                "Defina a variável de ambiente ou passe como argumento."
            )
        
        # Configura a API do Gemini
        genai.configure(api_key=self.api_key)
        
        # Inicializa o modelo com system_instruction
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=self.SYSTEM_INSTRUCTION
        )
        
        # Cria sessão de chat
        self.chat_session = self.model.start_chat(history=[])
        
        # Histórico de mensagens (mantém formato da API Gemini)
        self.historico = []
        
        # Configurações de limite
        self.max_historico = 20
        
        # Rastreamento de tokens na sessão
        self.total_tokens_entrada = 0
        self.total_tokens_saida = 0
        self.total_mensagens_processadas = 0
        
        # Timestamps
        self.primeira_mensagem = None
        self.ultima_mensagem = None
        
        print("✅ AssistantBrain inicializado com sucesso!")
        print(f"   Modelo: gemini-1.5-flash")
        print(f"   Máximo de histórico: {self.max_historico} mensagens")

    def processar(self, mensagem: str) -> dict:
        """
        Processa uma mensagem do usuário através da Gemini API.
        
        Args:
            mensagem (str): Texto enviado pelo usuário.
        
        Returns:
            dict: {
                "resposta": str,
                "tokens_entrada": int,
                "tokens_saida": int,
                "total_mensagens_historico": int,
                "status": str
            }
        
        Raises:
            Exception: Se houver erro na chamada da API.
        """
        try:
            # Registra timestamp da primeira mensagem
            if self.primeira_mensagem is None:
                self.primeira_mensagem = datetime.now()
            
            # Atualiza última mensagem
            self.ultima_mensagem = datetime.now()
            
            # Incrementa contador
            self.total_mensagens_processadas += 1
            
            # Envia mensagem para a API Gemini via chat.send_message()
            resposta = self.chat_session.send_message(mensagem)
            
            # Extrai texto da resposta
            texto_resposta = resposta.text
            
            # Extrai contagem de tokens do usage_metadata
            if hasattr(resposta, 'usage_metadata') and resposta.usage_metadata:
                tokens_entrada = resposta.usage_metadata.prompt_token_count
                tokens_saida = resposta.usage_metadata.candidates_token_count
            else:
                # Fallback se usage_metadata não estiver disponível
                tokens_entrada = 0
                tokens_saida = 0
            
            # Atualiza contadores totais de tokens
            self.total_tokens_entrada += tokens_entrada
            self.total_tokens_saida += tokens_saida
            
            # Adiciona mensagens ao histórico local
            # (O chat_session já mantém seu próprio histórico)
            self.historico.append({
                "role": "user",
                "parts": [{"text": mensagem}]
            })
            self.historico.append({
                "role": "model",
                "parts": [{"text": texto_resposta}]
            })
            
            # Limita o histórico a max_historico mensagens
            if len(self.historico) > self.max_historico:
                mensagens_a_remover = len(self.historico) - self.max_historico
                self.historico = self.historico[mensagens_a_remover:]
            
            return {
                "resposta": texto_resposta,
                "tokens_entrada": tokens_entrada,
                "tokens_saida": tokens_saida,
                "total_mensagens_historico": len(self.historico) // 2,  # Divide por 2 (user + model)
                "status": "sucesso"
            }
        
        except Exception as e:
            print(f"❌ Erro ao processar mensagem: {str(e)}")
            return {
                "resposta": f"Desculpe, ocorreu um erro: {str(e)}",
                "tokens_entrada": 0,
                "tokens_saida": 0,
                "total_mensagens_historico": len(self.historico) // 2,
                "status": "erro"
            }

    def limpar_historico(self) -> dict:
        """
        Limpa o histórico de conversa e reinicia a sessão de chat.
        
        Returns:
            dict: {
                "status": str,
                "mensagem": str,
                "mensagens_anteriores": int
            }
        """
        try:
            mensagens_anteriores = len(self.historico) // 2
            
            # Reinicia a sessão de chat
            self.chat_session = self.model.start_chat(history=[])
            self.historico = []
            
            # Reseta contadores (mas mantém totais da sessão anterior)
            # Se quiser resetar tudo, descomente as linhas abaixo:
            # self.total_tokens_entrada = 0
            # self.total_tokens_saida = 0
            # self.total_mensagens_processadas = 0
            # self.primeira_mensagem = None
            
            return {
                "status": "sucesso",
                "mensagem": "Histórico de conversa limpo com sucesso.",
                "mensagens_anteriores": mensagens_anteriores
            }
        
        except Exception as e:
            print(f"❌ Erro ao limpar histórico: {str(e)}")
            return {
                "status": "erro",
                "mensagem": f"Erro ao limpar histórico: {str(e)}",
                "mensagens_anteriores": len(self.historico) // 2
            }

    def get_stats(self) -> dict:
        """
        Retorna estatísticas da sessão atual.
        
        Returns:
            dict: {
                "total_mensagens_sessao": int,
                "tokens_entrada_estimado": int,
                "tokens_saida_estimado": int,
                "total_tokens_estimado": int,
                "primeira_mensagem": str (ISO format),
                "ultima_mensagem": str (ISO format),
                "duracao_sessao_minutos": float,
                "status": str
            }
        """
        try:
            # Calcula duração da sessão
            duracao_minutos = 0.0
            if self.primeira_mensagem and self.ultima_mensagem:
                duracao = self.ultima_mensagem - self.primeira_mensagem
                duracao_minutos = duracao.total_seconds() / 60
            
            return {
                "total_mensagens_sessao": self.total_mensagens_processadas,
                "tokens_entrada_estimado": self.total_tokens_entrada,
                "tokens_saida_estimado": self.total_tokens_saida,
                "total_tokens_estimado": self.total_tokens_entrada + self.total_tokens_saida,
                "primeira_mensagem": self.primeira_mensagem.isoformat() if self.primeira_mensagem else None,
                "ultima_mensagem": self.ultima_mensagem.isoformat() if self.ultima_mensagem else None,
                "duracao_sessao_minutos": round(duracao_minutos, 2),
                "historico_atual": len(self.historico) // 2,
                "max_historico_permitido": self.max_historico,
                "status": "sucesso"
            }
        
        except Exception as e:
            print(f"❌ Erro ao gerar estatísticas: {str(e)}")
            return {
                "status": "erro",
                "mensagem": f"Erro ao gerar estatísticas: {str(e)}"
            }


# Teste rápido (opcional)
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 Teste do AssistantBrain (Gemini)")
    print("="*60 + "\n")
    
    try:
        # Inicializa o brain
        brain = AssistantBrain()
        
        # Processa uma mensagem de teste
        print("📝 Enviando mensagem de teste...\n")
        resultado = brain.processar("Olá! Como você se chama?")
        
        print(f"🤖 Resposta:\n{resultado['resposta']}\n")
        print(f"📊 Tokens entrada: {resultado['tokens_entrada']}")
        print(f"📊 Tokens saída: {resultado['tokens_saida']}")
        print(f"💬 Total mensagens no histórico: {resultado['total_mensagens_historico']}\n")
        
        # Obtém estatísticas
        stats = brain.get_stats()
        print("📈 Estatísticas da Sessão:")
        for chave, valor in stats.items():
            print(f"   {chave}: {valor}")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
