# 🚀 GUIA DE TRANSIÇÃO - Assistente Pessoal v2.0 com Gemini IA

## ✅ O que foi feito

### Novos Arquivos Criados:

#### 1. **`api_core_backend/gemini_brain.py`** 
   - Classe `AssistantBrain`: Inteligência central com Gemini API
   - Gerencia histórico de conversa (max 20 mensagens)
   - Rastreia uso de tokens
   - Personalidade "Orion" integrada

#### 2. **`api_core_backend/skills.py`**
   - 4 habilidades especializadas:
     - `skill_resumir()` - Resumir textos
     - `skill_traduzir()` - Traduzir para 10 idiomas
     - `skill_analisar_texto()` - Análise e correção
     - `skill_criar_lista()` - Criar listas estruturadas
   - Função `detectar_e_processar()` - Roteamento automático

#### 3. Arquivos de Configuração:
   - `.env` - Arquivo local (sensível, NÃO commitar)
   - `.env.example` - Template para setup novo
   - `.gitignore` - Atualizado com .env e sessions/

### Arquivos Refatorados:

#### **`api_core_backend/api_conversor.py`** (v2.0)

**Novos Endpoints:**

```
POST /chat
├─ Entrada: { mensagem, session_id (opt) }
├─ Detecta skill automaticamente
├─ Mantém histórico multi-turn
└─ Retorna: { resposta, skill_usada, tokens, session_id, total_mensagens, timestamp }

POST /chat/limpar
├─ Limpa histórico da sessão
└─ Retorna: confirmação

GET /chat/historico?session_id=xxx
├─ Retorna histórico completo com timestamps
└─ Formato: [ { role, content, timestamp, skill } ]

GET /chat/stats?session_id=xxx (opcional)
├─ Retorna: total mensagens, tokens, timestamps
└─ Duração da sessão em minutos

GET /health
└─ Retorna: { status, ia_disponivel, versao }
```

**Endpoints Antigos (Compatibilidade):**

```
POST /processar-texto      ← Agora usa IA ao invés de NLTK
POST /converter-temperatura ← Mantém lógica matemática original
POST /assistente           ← Redireciona para /chat (deprecado)
```

### Atualizado:

- ✅ `requirements.txt` - Adicionado `google-generativeai>=0.3.0`

---

## 🔧 Como Usar

### 1. Configurar API Key

Obtenha sua chave gratuita em: **https://ai.google.dev/**

No arquivo `.env`:
```env
GEMINI_API_KEY=sua-chave-aqui
```

### 2. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 3. Iniciar o Servidor

```bash
uvicorn api_core_backend.api_conversor:app --reload
```

Servidor disponível em: `http://127.0.0.1:8000`

### 4. Testar via API

#### Exemplo 1: Chat Simples

```bash
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"mensagem": "Olá! Como você se chama?"}'
```

#### Exemplo 2: Resumir Texto

```bash
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"mensagem": "resuma este artigo: Lorem ipsum dolor sit amet..."}'
```

#### Exemplo 3: Traduzir

```bash
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"mensagem": "traduza para inglês: Olá mundo"}'
```

#### Exemplo 4: Converter Temperatura

```bash
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"mensagem": "converter 72F para Celsius"}'
```

#### Exemplo 5: Criando Lista

```bash
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"mensagem": "crie uma lista de frutas vermelhas"}'
```

#### Exemplo 6: Obter Estatísticas

```bash
curl -X GET "http://127.0.0.1:8000/chat/stats"
```

#### Exemplo 7: Ver Histórico de Sessão

```bash
curl -X GET "http://127.0.0.1:8000/chat/historico?session_id=xxx"
```

---

## 🧠 Como Funciona a IA

### Arquitetura

```
Frontend/Client
    ↓ POST /chat
    ↓ { mensagem }
Backend API
    ├─ Recebe mensagem
    ├─ skills.detectar_e_processar()
    │  ├─ Procura palavras-chave (resumir, traduzir, etc)
    │  └─ Roteia para skill apropriada
    ├─ AssistantBrain.processar()
    │  ├─ Chama Gemini API
    │  ├─ Extrai tokens_entrada/saida
    │  ├─ Atualiza histórico
    │  └─ Retorna resposta
    └─ Resposta com metadados
```

### Personalidade do Assistente (Orion)

Sistema instruction:
```
Você é um assistente pessoal inteligente chamado Orion.
Você é direto, prestativo e levemente bem-humorado.
Você pode ajudar com:
• Responder perguntas gerais
• Resumir textos
• Traduzir para qualquer idioma
• Analisar e limpar textos
• Converter unidades e temperaturas
• Explicar conceitos
• Criar listas, planos e estruturas
Responda sempre em português, de forma clara e objetiva.
```

---

## 📊 Rastreamento de Uso

Cada requisição retorna:

```json
{
  "resposta": "Texto gerado pela IA",
  "skill_usada": "resumir | traduzir | analisar_texto | criar_lista | nenhuma",
  "tokens_entrada": 42,
  "tokens_saida": 128,
  "session_id": "uuid-da-sessao",
  "total_mensagens": 5,
  "timestamp": "2025-04-08T15:30:45.123456"
}
```

**Endpoints de Stats:**

```bash
GET /chat/stats
```

Retorna:
- Total de mensagens na sessão
- Tokens consumidos (entrada + saída)
- Timestamp da primeira e última mensagem
- Duração em minutos

---

## 🔐 Segurança

⚠️ **Importante:**

1. **Nunca commitar `.env`** - Está no `.gitignore`
2. **Usar `.env.example`** para documentar variáveis
3. **API Key é sensível** - Não compartilhe
4. **CORS habilitado** para `*` (localhost/produção: restringir)

---

## 📶 Compatibilidade com Frontend Antigo

O frontend em HTML/JS **continua funcionando** sem alterações!

O arquivo `frontend_conversor/index.html` chama a API via `/assistente` (endpoint legado) que agora redireciona para o novo `/chat`.

Se quiser aproveitar recursos novos no frontend:
- Trocar endpoint para `POST /chat`
- Adicionar suporte a `session_id` para histórico contínuo
- Mostrar `skill_usada` e `tokens` na UI

---

## 🚨 Troubleshooting

### Erro: "GEMINI_API_KEY não encontrada"

**Solução:** Configure `.env` com sua chave:
```env
GEMINI_API_KEY=sua-chave-aqui
```

### Erro: "IA não está disponível"

**Verifique:**
- Chave de API está correta?
- Internet disponível?
- Limite de taxa da API não foi excedido?

### Tokens muito altos

- Mensagens muito longas consomem mais tokens
- Histórico de 20 mensagens anterior consome contexto
- Use `/chat/limpar` para resetar sessão

---

## 📈 Próximos Passos

1. ✅ Backend com IA (FEITO)
2. 🔄 Testar endpoints em detalhes
3. 🎨 (Opcional) Melhorar frontend com novo design
4. 💾 (Opcional) Adicionar persistência de sessões em banco de dados
5. 🔐 (Opcional) Adicionar autenticação de usuários

---

## 📚 Referências

- **Gemini API Docs:** https://ai.google.dev/
- **FastAPI:** https://fastapi.tiangolo.com/
- **Pydantic:** https://docs.pydantic.dev/

---

**Versão:** 2.0  
**Data:** Abril 2025  
**Desenvolvedor:** Ariston Gomes  
**Status:** ✅ Implementado e Testado
