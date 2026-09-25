"""
API Backend do Assistente Pessoal com IA (Gemini)
==================================================

Backend FastAPI que integra:
- AssistantBrain: Inteligência com Gemini API
- Skills: Detecção de intenção e roteamento
- Gerenciamento de sessões de conversa
- Retrocompatibilidade com endpoints antigos

Versão: 2.0 (com IA integrada)
Autor: Ariston Gomes
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime
import uvicorn
import re
import uuid

from api_core_backend.gemini_brain import AssistantBrain
from api_core_backend.skills import detectar_e_processar

# ============================================================================
# CONFIGURAÇÃO BÁSICA
# ============================================================================

app = FastAPI(title="Assistente Pessoal com IA", version="2.0")

# Variável global para o brain (singleton)
assistant_brain: Optional[AssistantBrain] = None

# Gerenciador de sessões (session_id -> historico)
sessions: Dict[str, dict] = {}

VERSION = "2.0"
IA_DISPONIVEL = False

# Configuração CORS (Permite que o Frontend se conecte)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# MODELOS PYDANTIC
# ============================================================================

class ChatRequest(BaseModel):
    """Modelo para requisições de chat"""
    mensagem: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    """Modelo para respostas de chat"""
    resposta: str
    skill_usada: str
    tokens_entrada: int
    tokens_saida: int
    session_id: str
    total_mensagens: int
    timestamp: str

class HealthResponse(BaseModel):
    """Modelo para resposta de health check"""
    status: str
    ia_disponivel: bool
    versao: str

class StatsResponse(BaseModel):
    """Modelo para estatísticas da sessão"""
    total_mensagens: int
    tokens_entrada: int
    tokens_saida: int
    total_tokens: int
    primeira_mensagem: Optional[str]
    ultima_mensagem: Optional[str]
    duracao_minutos: float

# ============================================================================
# INICIALIZAÇÃO
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Inicializa o brain (AssistantBrain) e carrega configurações"""
    global assistant_brain, IA_DISPONIVEL
    
    print("\n" + "="*60)
    print("🚀 Inicializando Assistente Pessoal com IA")
    print("="*60 + "\n")
    
    try:
        print("🧠 Carregando AssistantBrain (Gemini)...")
        assistant_brain = AssistantBrain()
        IA_DISPONIVEL = True
        print("✅ AssistantBrain carregado com sucesso!\n")
    except Exception as e:
        print(f"❌ Erro ao inicializar AssistantBrain: {e}")
        print("⚠️ IA não disponível. Endpoints de chat não funcionarão.\n")
        IA_DISPONIVEL = False

class UserInput(BaseModel):
    """Compatibilidade com versão antiga"""
    texto: str

# ============================================================================
# ENDPOINTS - HEALTH CHECK
# ============================================================================

@app.get("/", response_model=HealthResponse)
async def health_check():
    """
    Health check básico da API.
    Verifica se o servidor está rodando e se a IA está disponível.
    """
    return HealthResponse(
        status="online" if assistant_brain else "offline",
        ia_disponivel=IA_DISPONIVEL,
        versao=VERSION
    )

@app.get("/health", response_model=HealthResponse)
async def health_detailed():
    """
    Health check detalhado com informações sobre a IA.
    """
    return HealthResponse(
        status="online" if assistant_brain else "offline",
        ia_disponivel=IA_DISPONIVEL,
        versao=VERSION
    )

# ============================================================================
# ENDPOINTS - CHAT COM IA (NOVOS)
# ============================================================================

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Endpoint principal: entra com IA integrada.
    
    Fluxo:
    1. Recebe mensagem e session_id (opcional)
    2. Detecta skill via skills.detectar_e_processar()
    3. Processa via AssistantBrain
    4. Gerencia histórico de sessão
    5. Retorna resposta com metadados
    
    Request:
        mensagem: str - Mensagem do usuário
        session_id: str (opcional) - ID da sessão para histórico contínuo
    
    Response:
        resposta: str - Resposta da IA
        skill_usada: str - Qual skill foi acionada ("resumir", "traduzir", etc)
        tokens_entrada: int - Tokens usados de entrada
        tokens_saida: int - Tokens usados de saída
        session_id: str - ID da sessão
        total_mensagens: int - Total de mensagens nesta sessão
        timestamp: str - Data/hora do processamento
    """
    
    if not IA_DISPONIVEL or not assistant_brain:
        return ChatResponse(
            resposta="❌ IA não está disponível. Verifique a chave de API.",
            skill_usada="nenhuma",
            tokens_entrada=0,
            tokens_saida=0,
            session_id="erro",
            total_mensagens=0,
            timestamp=datetime.now().isoformat()
        )
    
    # Cria ou recupera session_id
    session_id = request.session_id or str(uuid.uuid4())
    
    if session_id not in sessions:
        sessions[session_id] = {
            "mensagens": [],
            "criada_em": datetime.now().isoformat()
        }
    
    try:
        # Detecta skill e processa
        resultado = detectar_e_processar(request.mensagem, assistant_brain)
        
        # Adiciona ao histórico da sessão
        sessions[session_id]["mensagens"].append({
            "role": "usuario",
            "conteudo": request.mensagem,
            "timestamp": datetime.now().isoformat()
        })
        sessions[session_id]["mensagens"].append({
            "role": "assistente",
            "conteudo": resultado["resposta"],
            "skill": resultado["skill_usada"],
            "timestamp": datetime.now().isoformat()
        })
        
        return ChatResponse(
            resposta=resultado["resposta"],
            skill_usada=resultado["skill_usada"],
            tokens_entrada=resultado["tokens_entrada"],
            tokens_saida=resultado["tokens_saida"],
            session_id=session_id,
            total_mensagens=len([m for m in sessions[session_id]["mensagens"] if m["role"] == "usuario"]),
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        print(f"❌ Erro ao processar chat: {e}")
        return ChatResponse(
            resposta=f"Desculpe, ocorreu um erro: {str(e)}",
            skill_usada="nenhuma",
            tokens_entrada=0,
            tokens_saida=0,
            session_id=session_id,
            total_mensagens=len([m for m in sessions[session_id]["mensagens"] if m["role"] == "usuario"]),
            timestamp=datetime.now().isoformat()
        )

@app.post("/chat/limpar")
async def limpar_chat(request: ChatRequest):
    """
    Limpa o histórico de conversa de uma sessão.
    
    Request:
        session_id: str - ID da sessão a limpar
    
    Response:
        status: str
        mensagem: str
        mensagens_limpas: int
    """
    
    if not IA_DISPONIVEL or not assistant_brain:
        return {
            "status": "erro",
            "mensagem": "IA não está disponível",
            "mensagens_limpas": 0
        }
    
    session_id = request.session_id
    
    if not session_id or session_id not in sessions:
        return {
            "status": "erro",
            "mensagem": f"Sessão {session_id} não encontrada",
            "mensagens_limpas": 0
        }
    
    try:
        # Limpa o histórico do brain
        resultado_brain = assistant_brain.limpar_historico()
        
        # Limpa o histórico da sessão
        mensagens_limpas = len(sessions[session_id]["mensagens"])
        sessions[session_id]["mensagens"] = []
        
        return {
            "status": "sucesso",
            "mensagem": "Histórico limpo com sucesso",
            "mensagens_limpas": mensagens_limpas // 2
        }
    
    except Exception as e:
        print(f"❌ Erro ao limpar histórico: {e}")
        return {
            "status": "erro",
            "mensagem": str(e),
            "mensagens_limpas": 0
        }

@app.get("/chat/historico")
async def obter_historico(session_id: str):
    """
    Retorna o histórico completo de uma sessão.
    
    Query (URL):
        session_id: str - ID da sessão
    
    Response:
        historico: list[dict] - Lista de mensagens com role, conteúdo e timestamp
        total_mensagens: int
        session_id: str
        criada_em: str
    """
    
    if session_id not in sessions:
        return {
            "status": "erro",
            "mensagem": f"Sessão {session_id} não encontrada",
            "historico": []
        }
    
    sessionData = sessions[session_id]
    
    return {
        "status": "sucesso",
        "session_id": session_id,
        "criada_em": sessionData["criada_em"],
        "historico": sessionData["mensagens"],
        "total_mensagens": len([m for m in sessionData["mensagens"] if m["role"] == "usuario"])
    }

@app.get("/chat/stats")
async def obter_stats(session_id: Optional[str] = None):
    """
    Retorna estatísticas da sessão atual.
    
    Query (URL):
        session_id: str (opcional) - Se não fornecido, retorna stats do brain
    
    Response:
        total_mensagens: int
        tokens_entrada: int
        tokens_saida: int
        total_tokens: int
        primeira_mensagem: str (ISO format)
        ultima_mensagem: str (ISO format)
        duracao_minutos: float
    """
    
    if not IA_DISPONIVEL or not assistant_brain:
        return {
            "status": "erro",
            "mensagem": "IA não está disponível"
        }
    
    try:
        # Se session_id fornecido, retorna stats daquela sessão
        if session_id and session_id in sessions:
            sessionData = sessions[session_id]
            mensagens = [m for m in sessionData["mensagens"] if m["role"] == "usuario"]
            
            primeira = mensagens[0]["timestamp"] if mensagens else None
            ultima = mensagens[-1]["timestamp"] if mensagens else None
            
            return {
                "status": "sucesso",
                "total_mensagens": len(mensagens),
                "primeira_mensagem": primeira,
                "ultima_mensagem": ultima,
                "duracao_minutos": 0
            }
        
        # Senão, retorna stats do brain
        stats_brain = assistant_brain.get_stats()
        return {
            "status": "sucesso",
            **stats_brain
        }
    
    except Exception as e:
        return {
            "status": "erro",
            "mensagem": str(e)
        }

# ============================================================================
# ENDPOINTS - COMPATIBILIDADE (ANTIGOS, REFATORADOS COM IA)
# ============================================================================

@app.post("/processar-texto")
async def processar_texto(input_data: UserInput):
    """
    Endpoint legado: processa texto.
    
    Antes: Usava limpeza com NLTK
    Agora: Usa IA do Gemini para análise mais inteligente
    
    Request:
        texto: str
    
    Response:
        status: str
        acao: str
        resposta: str
    """
    
    if not IA_DISPONIVEL or not assistant_brain:
        return {
            "status": "erro",
            "acao": "processamento_texto",
            "resposta": "IA não disponível"
        }
    
    try:
        # Prompt para análise de texto
        prompt = f"""Analise o seguinte texto e forneça:
1. Um resumo breve
2. Principais palavras-chave
3. Tom/sentimento geral

Texto: {input_data.texto}

Responda de forma concisa e clara."""
        
        resultado = assistant_brain.processar(prompt)
        
        return {
            "status": "sucesso",
            "acao": "processamento_texto",
            "resposta": resultado["resposta"]
        }
    
    except Exception as e:
        return {
            "status": "erro",
            "acao": "processamento_texto",
            "resposta": str(e)
        }

@app.post("/converter-temperatura")
async def converter_temperatura(input_data: UserInput):
    """
    Endpoint legado: converte temperatura.
    
    Mantém a lógica matemática original (não precisa de IA).
    
    Request:
        texto: str (ex: "converter 72F para Celsius")
    
    Response:
        status: str
        acao: str
        resposta: str
    """
    
    try:
        # Tenta extrair números do texto
        numeros = re.findall(r'-?\d+\.?\d*', input_data.texto)
        
        if not numeros:
            return {
                "status": "erro",
                "acao": "conversao_temperatura",
                "resposta": "Não consegui encontrar uma temperatura no seu texto."
            }
        
        temp_valor = float(numeros[0])
        
        # Detecta unidade de origem
        texto_lower = input_data.texto.lower()
        
        if "fahrenheit" in texto_lower or "f" in texto_lower or "°f" in texto_lower:
            # F para C
            temp_convertida = (temp_valor - 32) * 5/9
            unidade_origem = "°F"
            unidade_destino = "°C"
        elif "celsius" in texto_lower or "c" in texto_lower or "°c" in texto_lower:
            # C para F
            temp_convertida = (temp_valor * 9/5) + 32
            unidade_origem = "°C"
            unidade_destino = "°F"
        else:
            return {
                "status": "erro",
                "acao": "conversao_temperatura",
                "resposta": "Especifique se é Fahrenheit (F) ou Celsius (C)."
            }
        
        resposta = f"{temp_valor}{unidade_origem} = {round(temp_convertida, 2)}{unidade_destino}"
        
        return {
            "status": "sucesso",
            "acao": "conversao_temperatura",
            "resposta": resposta
        }
    
    except Exception as e:
        return {
            "status": "erro",
            "acao": "conversao_temperatura",
            "resposta": f"Erro na conversão: {str(e)}"
        }

# ============================================================================
# ENDPOINT LEGADO (ANTIGO - MANTIDO PARA COMPATIBILIDADE)
# ============================================================================

@app.post("/assistente")
async def handle_assistant_request(input_data: UserInput):
    """
    Endpoint antigo do assistente.
    Agora redireciona para o novo sistema com IA.
    
    ⚠️ DESCONTINUADO: Use /chat em vez disso.
    """
    request = ChatRequest(mensagem=input_data.texto)
    return await chat(request)
