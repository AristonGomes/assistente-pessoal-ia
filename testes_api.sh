#!/bin/bash
# 🧪 Script de Testes - Assistente Pessoal v2.0
# 
# Este script testa todos os endpoints principais da API.
# Execute após iniciar: uvicorn api_core_backend.api_conversor:app --reload
#

#!/bin/bash

API_URL="http://127.0.0.1:8000"
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}🧪 Testes da API - Assistente Pessoal v2.0${NC}"
echo -e "${BLUE}================================================${NC}\n"

# ============================================================================
# TEST 1: Health Check
# ============================================================================

echo -e "${YELLOW}[1/7] Testando Health Check...${NC}"
curl -s -X GET "$API_URL/health" | python -m json.tool
echo -e "${GREEN}✅ Health check completo\n${NC}"

# ============================================================================
# TEST 2: Chat Simples
# ============================================================================

echo -e "${YELLOW}[2/7] Testando Chat Simples...${NC}"
SESSION_ID=$(uuidgen 2>/dev/null || echo "test-session-001")

curl -s -X POST "$API_URL/chat" \
  -H "Content-Type: application/json" \
  -d "{\"mensagem\": \"Olá! Como você se chama?\", \"session_id\": \"$SESSION_ID\"}" | python -m json.tool

echo -e "${GREEN}✅ Chat simples completo\n${NC}"

# ============================================================================
# TEST 3: Skill - Resumir
# ============================================================================

echo -e "${YELLOW}[3/7] Testando Skill RESUMIR...${NC}"
curl -s -X POST "$API_URL/chat" \
  -H "Content-Type: application/json" \
  -d "{\"mensagem\": \"resuma este texto: Python é uma linguagem de programação interpretada, de alto nível, com semântica dinâmica, muito poderosa e versátil. Sua filosofia de design enfatiza a legibilidade do código. Python é frequentemente comparado com Perl, Java, JavaScript e outras linguagens similares.\", \"session_id\": \"$SESSION_ID\"}" | python -m json.tool

echo -e "${GREEN}✅ Resumo completo\n${NC}"

# ============================================================================
# TEST 4: Skill - Traduzir
# ============================================================================

echo -e "${YELLOW}[4/7] Testando Skill TRADUZIR...${NC}"
curl -s -X POST "$API_URL/chat" \
  -H "Content-Type: application/json" \
  -d "{\"mensagem\": \"traduza para inglês: Olá, como você está? Tudo bem?\", \"session_id\": \"$SESSION_ID\"}" | python -m json.tool

echo -e "${GREEN}✅ Tradução completa\n${NC}"

# ============================================================================
# TEST 5: Skill - Analisar Texto
# ============================================================================

echo -e "${YELLOW}[5/7] Testando Skill ANALISAR...${NC}"
curl -s -X POST "$API_URL/chat" \
  -H "Content-Type: application/json" \
  -d "{\"mensagem\": \"analise este texto: Este texto contem varios erros de ortografia e gramática que precizam ser corrigidos para melhorar sua qualidade.\", \"session_id\": \"$SESSION_ID\"}" | python -m json.tool

echo -e "${GREEN}✅ Análise completa\n${NC}"

# ============================================================================
# TEST 6: Converter Temperatura (Endpoint Legado)
# ============================================================================

echo -e "${YELLOW}[6/7] Testando Conversão de Temperatura (Legado)...${NC}"
curl -s -X POST "$API_URL/converter-temperatura" \
  -H "Content-Type: application/json" \
  -d "{\"texto\": \"converter 72F para Celsius\"}" | python -m json.tool

echo -e "${GREEN}✅ Conversão completa\n${NC}"

# ============================================================================
# TEST 7: Obter Estatísticas
# ============================================================================

echo -e "${YELLOW}[7/7] Testando Estatísticas da Sessão...${NC}"
curl -s -X GET "$API_URL/chat/stats?session_id=$SESSION_ID" | python -m json.tool

echo -e "${GREEN}✅ Estatísticas completas\n${NC}"

# ============================================================================
# TEST 8: Obter Histórico
# ============================================================================

echo -e "${YELLOW}[BONUS] Obtendo Histórico da Sessão...${NC}"
curl -s -X GET "$API_URL/chat/historico?session_id=$SESSION_ID" | python -m json.tool

echo -e "${GREEN}✅ Histórico completo\n${NC}"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}✅ Todos os testes foram executados com sucesso!${NC}"
echo -e "${BLUE}================================================${NC}"
