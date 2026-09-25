# ⚡ Quick Start - Assistente Pessoal v2.0 com Gemini IA

## 🚀 5 Minutos para Começar

### 1️⃣ Obter API Key (2 minutos)

```bash
# Visite: https://ai.google.dev/
# Clique em "Get API Key"
# Copie a chave gerada (começa com sk-...)
```

### 2️⃣ Configurar Projeto (1 minuto)

```bash
cd c:\Users\arist\Desktop\Projetos\Python\assistente-pessoal-ia

# Copiar template
copy .env.example .env

# Editar .env (abra o arquivo)
# Preencha: GEMINI_API_KEY=sua-chave-aqui
```

### 3️⃣ Instalar Dependências (1 minuto)

```bash
pip install -r requirements.txt
```

### 4️⃣ Iniciar Servidor (1 minuto)

```bash
uvicorn api_core_backend.api_conversor:app --reload
```

**Saída esperada:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
🚀 Inicializando Assistente Pessoal com IA
✅ AssistantBrain carregado com sucesso!
```

### 5️⃣ Testar API (1 minuto)

```bash
# Em outro terminal:
curl -X GET "http://127.0.0.1:8000/health"
```

**Resposta esperada:**
```json
{
  "status": "online",
  "ia_disponivel": true,
  "versao": "2.0"
}
```

---

## 💬 Exemplos Rápidos

### Chat Simples

```bash
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"mensagem": "Olá! Como você se chama?"}'
```

### Resumir Texto

```bash
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"mensagem": "resuma: Python é uma linguagem de programação..."}'
```

### Traduzir

```bash
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"mensagem": "traduza para inglês: Olá mundo"}'
```

### Converter Temperatura

```bash
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"mensagem": "converter 72F para Celsius"}'
```

---

## 📊 Verificar Uso de Tokens

```bash
curl -X GET "http://127.0.0.1:8000/chat/stats"
```

---

## 📚 Documentação Completa

Leia os guias detalhados:
- **[GUIA_GEMINI_IA.md](GUIA_GEMINI_IA.md)** - Como usar tudo
- **[ARQUITETURA.md](ARQUITETURA.md)** - Detalhes técnicos
- **[RESUMO_IMPLEMENTACAO.md](RESUMO_IMPLEMENTACAO.md)** - O que foi feito

---

## 🆘 Troubleshooting

### ❌ "GEMINI_API_KEY não encontrada"

```bash
# Verifique se .env foi criado:
cat .env

# Verifique se contém sua chave:
grep GEMINI_API_KEY .env
```

### ❌ "Conexão Recusada"

```bash
# Servidor iniciado? Verifique porta 8000:
netstat -ano | findstr :8000

# Se não estiver rodando, execute:
uvicorn api_core_backend.api_conversor:app --reload
```

### ❌ "IA não disponível"

- Chave de API está correta?
- Internet disponível?
- Quota da API não excedida?

### ❌ "Resposta lenta"

Normal! Gemini leva 1-2 segundos.

---

## 🎯 Próximas Ações

1. ✅ Setup completo
2. ✅ Teste `/health`
3. ✅ Teste `/chat` com mensagem simples
4. ✅ Teste skills (resumir, traduzir)
5. 🔄 (Opcional) Atualizar frontend
6. 🔄 (Opcional) Adicionar persistência em BD

---

## 📞 Precisa de Ajuda?

Todos os endpoints têm:
- ✅ Validação Pydantic
- ✅ Error handling
- ✅ Resposta JSON válida
- ✅ Status code apropriado

**Testes disponíveis:**
```bash
bash testes_api.sh
```

---

**Versão:** 2.0  
**Status:** ✅ Pronto para Usar  
**Tempo Setup:** ~5 minutos
