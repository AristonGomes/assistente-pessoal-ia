# 📊 Visão Geral da Arquitetura - Assistente Pessoal v2.0

## 🏗️ Estrutura de Arquivos Atualizada

```
assistente-pessoal-ia/
│
├── 📄 README.md                              # Documentação original
├── 📄 GUIA_GEMINI_IA.md                     # ← NOVO: Guia de uso v2.0
├── 📄 ARQUITETURA.md                        # ← ESTE ARQUIVO
│
├── 🔐 .env                                  # ← NOVO: Config sensível (local)
├── 📋 .env.example                          # ← NOVO: Template de config
├── 🚫 .gitignore                            # ← ATUALIZADO: +.env, +sessions/
│
├── 📦 requirements.txt                       # ← ATUALIZADO: +google-generativeai
│
├── 📂 api_core_backend/
│   ├── __init__.py
│   │
│   ├── 🧠 api_conversor.py                  # ← REFATORADO v2.0
│   │   ├─ Novos endpoints: /chat, /chat/*, /health
│   │   ├─ Endpoints legados: /processar-texto, /converter-temperatura
│   │   ├─ Integração com AssistantBrain
│   │   └─ Gerenciamento de sessões
│   │
│   ├── 🤖 gemini_brain.py                   # ← NOVO: Core da IA
│   │   ├─ Classe AssistantBrain
│   │   ├─ Integração Gemini API
│   │   ├─ Histórico de conversa
│   │   └─ Rastreamento de tokens
│   │
│   ├── ⚡ skills.py                         # ← NOVO: Skills especializados
│   │   ├─ skill_resumir()
│   │   ├─ skill_traduzir()
│   │   ├─ skill_analisar_texto()
│   │   ├─ skill_criar_lista()
│   │   └─ detectar_e_processar()
│   │
│   └── 📂 utils/
│       ├── __init__.py
│       └── text_processor.py                # (Legacy: NLTK - agora opcional)
│
├── 📂 config/
│   └── stopwords_extras.json                # (Legacy: agora opcional)
│
├── 📂 frontend_conversor/
│   └── index.html                           # ← Compatível (sem alterações)
│
└── 📂 sessions/                             # ← NOVO: (Gerado em runtime)
    └── {session_id}.json                   # Histórico de sessão

```

---

## 🔄 Fluxo de Requisição

```
╔═══════════════════════════════════════════════════════════════════════╗
║                        CLIENTE / FRONTEND                             ║
║  (HTML/JavaScript ou curl ou qualquer HTTP client)                   ║
╚═══════════════════════════════════════════════════════════════════════╝
                                    ↓
                     POST /chat {"mensagem": "..."}
                                    ↓
╔═══════════════════════════════════════════════════════════════════════╗
║                     FASTAPI BACKEND (api_conversor.py)               ║
║  ┌─────────────────────────────────────────────────────────────┐     ║
║  │ 1. Receber requisição POST /chat                            │     ║
║  │    ├─ message: str                                          │     ║
║  │    └─ session_id: str (optional)                           │     ║
║  └─────────────────────────────────────────────────────────────┘     ║
║                              ↓                                         ║
║  ┌─────────────────────────────────────────────────────────────┐     ║
║  │ 2. DETECTAR SKILL (skills.py)                              │     ║
║  │    ├─ Procura por palavras-chave                           │     ║
║  │    ├─ "resuma", "resumo de"     → skill_resumir()         │     ║
║  │    ├─ "traduza", "em inglês"    → skill_traduzir()        │     ║
║  │    ├─ "analise", "corrija"      → skill_analisar_texto()  │     ║
║  │    ├─ "crie uma lista", "liste" → skill_criar_lista()     │     ║
║  │    └─ Nenhuma palavra-chave     → processamento normal     │     ║
║  └─────────────────────────────────────────────────────────────┘     ║
║                              ↓                                         ║
║  ┌─────────────────────────────────────────────────────────────┐     ║
║  │ 3. CHAMAR A IA (gemini_brain.py)                            │     ║
║  │    ├─ AssistantBrain.processar(prompt)                     │     ║
║  │    ├─ Envia para Gemini API                                │     ║
║  │    ├─ Mantém histórico (max 20 msgs)                       │     ║
║  │    └─ Extrai tokens_entrada + tokens_saida                │     ║
║  └─────────────────────────────────────────────────────────────┘     ║
║                              ↓                                         ║
║  ┌─────────────────────────────────────────────────────────────┐     ║
║  │ 4. GERENCIAR SESSÃO (api_conversor.py)                     │     ║
║  │    ├─ Cria session_id se não existir                       │     ║
║  │    ├─ Adiciona mensagem ao histórico                       │     ║
║  │    └─ Mantém timestamps                                    │     ║
║  └─────────────────────────────────────────────────────────────┘     ║
║                              ↓                                         ║
║  ┌─────────────────────────────────────────────────────────────┐     ║
║  │ 5. RETORNAR RESPOSTA (JSON)                                │     ║
║  │    ├─ resposta: str                                        │     ║
║  │    ├─ skill_usada: str                                     │     ║
║  │    ├─ tokens_entrada: int                                  │     ║
║  │    ├─ tokens_saida: int                                    │     ║
║  │    ├─ session_id: str                                      │     ║
║  │    ├─ total_mensagens: int                                 │     ║
║  │    └─ timestamp: str (ISO)                                 │     ║
║  └─────────────────────────────────────────────────────────────┘     ║
╚═══════════════════════════════════════════════════════════════════════╝
                                    ↓
╔═══════════════════════════════════════════════════════════════════════╗
║                      CLIENTE RECEBE RESPOSTA                          ║
║  (Exibe na UI / Loga na console / etc)                                ║
╚═══════════════════════════════════════════════════════════════════════╝
```

---

## 🎯 Exemplo Real: Resumindo um Texto

```
┌─────────────────────────────────────────────────────────────────────┐
│ CLIENTE ENVIA:                                                      │
│                                                                     │
│ POST /chat HTTP/1.1                                                │
│ Content-Type: application/json                                      │
│                                                                     │
│ {                                                                   │
│   "mensagem": "resuma este texto: A IA é uma tecnologia que...",  │
│   "session_id": "abc-123"                                           │
│ }                                                                   │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ BACKEND PROCESSA:                                                   │
│                                                                     │
│ 1. Detecta "resuma" → Ativa skill_resumir()                        │
│ 2. Monta prompt: "Por favor, resuma... {texto}"                    │
│ 3. Chama: assistant_brain.processar(prompt)                        │
│ 4. Gemini responde com resumo estruturado                          │
│ 5. Extrai: tokens_entrada=45, tokens_saida=120                     │
│ 6. Salva no histórico da sessão abc-123                            │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ CLIENTE RECEBE:                                                     │
│                                                                     │
│ {                                                                   │
│   "resposta": "**Tema principal**: Inteligência Artificial...",    │
│   "skill_usada": "resumir",                                         │
│   "tokens_entrada": 45,                                             │
│   "tokens_saida": 120,                                              │
│   "session_id": "abc-123",                                          │
│   "total_mensagens": 1,                                             │
│   "timestamp": "2025-04-08T15:30:45.123456"                        │
│ }                                                                   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📝 Comparação: Antes vs Depois

| Aspecto | Antes (v1.0) | Depois (v2.0) |
|---------|------|-------|
| **Motor** | NLTK (Regex) | Gemini IA |
| **Capacidades** | Limpeza + Temp. conversa | 10+ funcionalidades inteligentes |
| **Histórico** | Não | Sim (20 msgs) |
| **Sessões** | Não | Sim (UUID) |
| **Tokens** | Não conta | Rastreado em tempo real |
| **Skills** | 2 regras fixas | 4+ habilidades + custom |
| **Idiomas** | PT-BR only | Qualquer idioma |
| **Frontend** | Compatível | 100% Compatível ✅ |

---

## 🔌 Integração Gemini API

```
┌─────────────────────────────────────────────────────────┐
│            AssistantBrain (gemini_brain.py)            │
├─────────────────────────────────────────────────────────┤
│ initialization:                                         │
│  ├─ genai.configure(api_key=GEMINI_API_KEY)           │
│  ├─ model = genai.GenerativeModel("gemini-1.5-flash")  │
│  └─ chat_session = model.start_chat(...)             │
│                                                          │
│ processar(mensagem):                                    │
│  ├─ response = chat_session.send_message(msg)         │
│  ├─ tokens_in = response.usage_metadata.prompt...     │
│  └─ tokens_out = response.usage_metadata.candidates...│
│                                                          │
│ limpar_historico():                                     │
│  └─ chat_session = model.start_chat([])            │
│                                                          │
│ get_stats():                                            │
│  ├─ total_mensagens                                     │
│  ├─ total_tokens (entrada + saída)                     │
│  └─ primeira_mensagem ... última_mensagem              │
└─────────────────────────────────────────────────────────┘
         ↓
         ↓ HTTPS
         ↓
┌─────────────────────────────────────────────────────────┐
│              Google Gemini API                          │
│  (https://generativelanguage.googleapis.com/v1beta/)  │
└─────────────────────────────────────────────────────────┘
```

---

## 🔐 Variáveis de Ambiente

```
.env (Local - NÃO COMMITAR)
│
├─ GEMINI_API_KEY=sk-...     # Sensível!
├─ MAX_CONVERSATION_HISTORY=20
├─ DEBUG=false
├─ HOST=127.0.0.1
└─ PORT=8000


.env.example (Commitado - Template)
│
├─ GEMINI_API_KEY=seu-gemini-api-key-aqui
├─ MAX_CONVERSATION_HISTORY=20
├─ DEBUG=false
├─ HOST=127.0.0.1
└─ PORT=8000
```

---

## 📈 Métricas e Monitoramento

Endpoints de monitoramento disponíveis:

```bash
# Health check
GET /health
→ { status, ia_disponivel, versao }

# Estatísticas da sessão
GET /chat/stats?session_id=xxx
→ { total_mensagens, tokens_entrada, tokens_saida, ... }

# Histórico completo
GET /chat/historico?session_id=xxx
→ { historico: [ { role, content, skill, timestamp } ] }
```

---

## 🚀 Deploy Checklist

- [ ] Copiar `.env.example` para `.env`
- [ ] Preencher `GEMINI_API_KEY` com chave real
- [ ] Rodar `pip install -r requirements.txt`
- [ ] Testar `/health` endpoint
- [ ] Testar `/chat` com mensagem simples
- [ ] Verificar consumo de tokens em `/chat/stats`
- [ ] Documentar limite de API quota
- [ ] (Prod) Restringir CORS para domínios específicos
- [ ] (Prod) Usar scheduler para limpar sessões antigas
- [ ] (Prod) Implementar rate limiting

---

**Versão:** 2.0  
**Última atualização:** Abril 2025  
**Status:** ✅ Pronto para Produção
