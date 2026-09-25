"""
Módulo: Skills do Assistente
=============================

Define habilidades especiais que o assistente detecta automaticamente
e trata com prompts otimizados. Cada skill é acionada por palavras-chave
específicas na mensagem do usuário.

Habilidades implementadas:
- skill_resumir: Resumir textos em tópicos
- skill_traduzir: Traduzir para diferentes idiomas
- skill_analisar_texto: Analisar, revisar e corrigir textos
- skill_criar_lista: Criar listas estruturadas em markdown
"""

import re
from typing import Optional


# ============================================================================
# PROMPTS OTIMIZADOS PARA CADA SKILL
# ============================================================================

PROMPT_RESUMIR = """Por favor, resuma o texto a seguir em TÓPICOS PRINCIPAIS.

Formato esperado:
- **Tema principal**: [identifique o assunto central]
- **Pontos-chave**:
  • [1º ponto importante]
  • [2º ponto importante]
  • [3º ponto importante]
  (máximo 5 pontos)

Texto a resumir:
{texto}

Seja conciso e objetivo."""

PROMPT_TRADUZIR = """Traduza o texto a seguir para {idioma}.

IMPORTANTE: Retorne APENAS a tradução, sem explicações ou prefácios.

Texto original:
{texto}"""

PROMPT_ANALISAR = """Analise o texto a seguir e forneça uma crítica construtiva.

Formato esperado:
- **Problemas encontrados**:
  • [problema 1]
  • [problema 2]
  ...

- **Versão corrigida**:
  [texto revisado e melhorado]

- **Sugestões**:
  • [sugestão 1]
  • [sugestão 2]

Texto a analisar:
{texto}"""

PROMPT_LISTA = """Crie uma lista estruturada em markdown baseada na solicitação do usuário.

Solicitação:
{solicitacao}

Formato esperado:
# [Título da Lista]

## [Subcategoria 1]
- [ ] [Item 1]
- [ ] [Item 2]
...

## [Subcategoria 2]
...

(Use checkboxes se for lista de tarefas, use números se for ranking/ordem)"""

# ============================================================================
# FUNÇÕES SKILL
# ============================================================================


def skill_resumir(texto: str, brain) -> dict:
    """
    Skill para resumir textos em tópicos principais.
    
    Args:
        texto (str): Texto a ser resumido
        brain: Instância de AssistantBrain
    
    Returns:
        dict: {
            "resposta": str,
            "skill_usada": str,
            "tokens_entrada": int,
            "tokens_saida": int
        }
    """
    prompt = PROMPT_RESUMIR.format(texto=texto)
    
    resultado = brain.processar(prompt)
    
    return {
        "resposta": resultado["resposta"],
        "skill_usada": "resumir",
        "tokens_entrada": resultado["tokens_entrada"],
        "tokens_saida": resultado["tokens_saida"]
    }


def skill_traduzir(mensagem: str, texto: str, brain) -> dict:
    """
    Skill para traduzir textos para diferentes idiomas.
    
    Detecta o idioma alvo automaticamente à partir da mensagem.
    
    Args:
        mensagem (str): Mensagem original (contém indicação do idioma)
        texto (str): Texto a ser traduzido
        brain: Instância de AssistantBrain
    
    Returns:
        dict: {
            "resposta": str,
            "skill_usada": str,
            "tokens_entrada": int,
            "tokens_saida": int,
            "idioma_detectado": str
        }
    """
    # Detecta idioma alvo
    mapa_idiomas = {
        "inglês": "English",
        "english": "English",
        "espanhol": "Spanish",
        "spanish": "Spanish",
        "francês": "French",
        "french": "French",
        "italiano": "Italian",
        "german": "German",
        "alemão": "German",
        "japonês": "Japanese",
        "japanese": "Japanese",
        "chinês": "Chinese",
        "chinese": "Chinese",
        "russo": "Russian",
        "russian": "Russian",
        "árabe": "Arabic",
        "arabic": "Arabic",
    }
    
    idioma_detectado = "English"  # padrão
    mensagem_lower = mensagem.lower()
    
    for keyword, idioma in mapa_idiomas.items():
        if keyword in mensagem_lower:
            idioma_detectado = idioma
            break
    
    prompt = PROMPT_TRADUZIR.format(idioma=idioma_detectado, texto=texto)
    
    resultado = brain.processar(prompt)
    
    return {
        "resposta": resultado["resposta"],
        "skill_usada": "traduzir",
        "tokens_entrada": resultado["tokens_entrada"],
        "tokens_saida": resultado["tokens_saida"],
        "idioma_detectado": idioma_detectado
    }


def skill_analisar_texto(texto: str, brain) -> dict:
    """
    Skill para analisar, revisar e corrigir textos.
    
    Fornece crítica construtiva e versão melhorada do texto.
    
    Args:
        texto (str): Texto a ser analisado
        brain: Instância de AssistantBrain
    
    Returns:
        dict: {
            "resposta": str,
            "skill_usada": str,
            "tokens_entrada": int,
            "tokens_saida": int
        }
    """
    prompt = PROMPT_ANALISAR.format(texto=texto)
    
    resultado = brain.processar(prompt)
    
    return {
        "resposta": resultado["resposta"],
        "skill_usada": "analisar_texto",
        "tokens_entrada": resultado["tokens_entrada"],
        "tokens_saida": resultado["tokens_saida"]
    }


def skill_criar_lista(solicitacao: str, brain) -> dict:
    """
    Skill para criar listas estruturadas em markdown.
    
    Cria listas bem formatadas de acordo com a solicitação do usuário.
    
    Args:
        solicitacao (str): Descrição do tipo de lista desejada
        brain: Instância de AssistantBrain
    
    Returns:
        dict: {
            "resposta": str,
            "skill_usada": str,
            "tokens_entrada": int,
            "tokens_saida": int
        }
    """
    prompt = PROMPT_LISTA.format(solicitacao=solicitacao)
    
    resultado = brain.processar(prompt)
    
    return {
        "resposta": resultado["resposta"],
        "skill_usada": "criar_lista",
        "tokens_entrada": resultado["tokens_entrada"],
        "tokens_saida": resultado["tokens_saida"]
    }


# ============================================================================
# DETECÇÃO E ROTEAMENTO DE SKILLS
# ============================================================================

def _extrair_texto_apos_skill(mensagem: str, palavras_chave: list) -> Optional[str]:
    """
    Extrai o texto/conteúdo após as palavras-chave de uma skill.
    
    Exemplo: "resuma este texto: Lorem ipsum dolor sit amet"
    Retorna: "Lorem ipsum dolor sit amet"
    
    Args:
        mensagem (str): Mensagem do usuário
        palavras_chave (list): Lista de palavras-chave a procurar
    
    Returns:
        str: Texto extraído, ou None se não encontrar
    """
    mensagem_lower = mensagem.lower()
    
    for keyword in palavras_chave:
        padrao = rf"{re.escape(keyword)}\s*:?\s*(.*)"
        match = re.search(padrao, mensagem_lower, re.IGNORECASE | re.DOTALL)
        if match:
            texto = match.group(1).strip()
            if texto:
                return texto
    
    return None


def detectar_e_processar(mensagem: str, brain) -> dict:
    """
    Função principal que detecta a intenção e roteia para a skill apropriada.
    
    Fluxo:
    1. Verifica se mensagem ativa alguma skill específica
    2. Se sim, extrai o conteúdo e chama a skill
    3. Se não, chama brain.processar() normalmente
    
    Args:
        mensagem (str): Mensagem do usuário
        brain: Instância de AssistantBrain
    
    Returns:
        dict: {
            "resposta": str,
            "skill_usada": str,
            "tokens_entrada": int,
            "tokens_saida": int,
            "status": str
        }
    """
    
    mensagem_lower = mensagem.lower()
    
    # ========== SKILL 1: RESUMIR ==========
    if any(keyword in mensagem_lower for keyword in ["resuma", "resumo de", "resume"]):
        print("🎯 Skill detectada: RESUMIR")
        
        # Tenta extrair o texto a sumarizar
        texto = _extrair_texto_apos_skill(
            mensagem,
            ["resuma", "resumo de", "resume"]
        )
        
        # Se não conseguiu extrair, usa a mensagem inteira
        if not texto:
            # Remove as palavras-chave e usa o resto
            texto = re.sub(
                r"(resuma|resumo de|resume)\s*:?\s*",
                "",
                mensagem,
                flags=re.IGNORECASE
            ).strip()
        
        if texto and len(texto) > 20:  # Mínimo de caracteres
            resultado = skill_resumir(texto, brain)
            resultado["status"] = "sucesso"
            return resultado
    
    # ========== SKILL 2: TRADUZIR ==========
    if any(keyword in mensagem_lower for keyword in [
        "traduza", "traduz", "em inglês", "em espanhol", 
        "em francês", "em italiano", "em alemão", "em japonês",
        "translate", "traducir"
    ]):
        print("🎯 Skill detectada: TRADUZIR")
        
        # Tenta extrair o texto a traduzir
        texto = _extrair_texto_apos_skill(
            mensagem,
            ["traduza", "traduz", "translate"]
        )
        
        # Se não conseguiu, extrai após "em [idioma]"
        if not texto:
            match = re.search(r"em\s+(?:inglês|english|espanhol|spanish|.*?):\s*(.*)", 
                            mensagem, re.IGNORECASE | re.DOTALL)
            if match:
                texto = match.group(1).strip()
        
        # Como último recurso, tira as palavras-chave
        if not texto:
            texto = re.sub(
                r"(traduza|traduz|em\s+(?:inglês|english|espanhol|spanish|.*?))\s*:?\s*",
                "",
                mensagem,
                flags=re.IGNORECASE
            ).strip()
        
        if texto and len(texto) > 5:
            resultado = skill_traduzir(mensagem, texto, brain)
            resultado["status"] = "sucesso"
            return resultado
    
    # ========== SKILL 3: ANALISAR TEXTO ==========
    if any(keyword in mensagem_lower for keyword in [
        "analise", "corrija", "melhore o texto", "revise",
        "crítica", "analisa", "revisa"
    ]):
        print("🎯 Skill detectada: ANALISAR TEXTO")
        
        # Tenta extrair o texto a analisar
        texto = _extrair_texto_apos_skill(
            mensagem,
            ["analise", "corrija", "melhore", "revise"]
        )
        
        # Como fallback, remove palavras-chave
        if not texto:
            texto = re.sub(
                r"(analise|corrija|melhore o texto|revise)\s*:?\s*",
                "",
                mensagem,
                flags=re.IGNORECASE
            ).strip()
        
        if texto and len(texto) > 20:
            resultado = skill_analisar_texto(texto, brain)
            resultado["status"] = "sucesso"
            return resultado
    
    # ========== SKILL 4: CRIAR LISTA ==========
    if any(keyword in mensagem_lower for keyword in [
        "crie uma lista", "liste", "enumere", "create a list",
        "liste tudo", "faça uma lista"
    ]):
        print("🎯 Skill detectada: CRIAR LISTA")
        
        # Remove as palavras-chave para obter a solicitação
        solicitacao = re.sub(
            r"(crie uma lista|liste|enumere|create a list|faça uma lista)\s*:?\s*(?:de\s+)?",
            "",
            mensagem,
            flags=re.IGNORECASE
        ).strip()
        
        if solicitacao and len(solicitacao) > 5:
            resultado = skill_criar_lista(solicitacao, brain)
            resultado["status"] = "sucesso"
            return resultado
    
    # ========== NENHUMA SKILL ESPECÍFICA: PROCESSAMENTO NORMAL ==========
    print("ℹ️ Nenhuma skill detectada, usando processamento padrão")
    resultado = brain.processar(mensagem)
    
    return {
        "resposta": resultado["resposta"],
        "skill_usada": "nenhuma",
        "tokens_entrada": resultado["tokens_entrada"],
        "tokens_saida": resultado["tokens_saida"],
        "status": "sucesso"
    }


# ============================================================================
# TESTE (Opcional)
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 Teste do Módulo Skills")
    print("="*60 + "\n")
    
    # Este teste requer una instância de brain funcionando
    print("ℹ️ Para testar as skills, importe e use:\n")
    print("   from api_core_backend.gemini_brain import AssistantBrain")
    print("   from api_core_backend.skills import detectar_e_processar")
    print()
    print("   brain = AssistantBrain()")
    print("   resultado = detectar_e_processar('resuma este texto: ...', brain)")
    print()
