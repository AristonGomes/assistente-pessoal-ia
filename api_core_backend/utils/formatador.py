"""
Módulo: Formatadores e Utilitários
===================================

Funções auxiliares para formatação de respostas, gerenciamento de histórico
e estimativa de custos de uso da Gemini API.
"""

import re
from typing import List, Dict, Optional


def formatar_resposta_telegram(texto: str) -> str:
    """
    Escapa caracteres especiais de markdown para uso seguro em bots Telegram.
    
    Telegram suporta MarkdownV2 que requer escape de vários caracteres.
    Esta função prepara o texto para envio seguro em bots.
    
    Args:
        texto (str): Texto original da resposta da IA
    
    Returns:
        str: Texto com caracteres escapados para Telegram MarkdownV2
    
    Exemplo:
        >>> texto = "Olá *mundo* com _ênfase_!"
        >>> formatar_resposta_telegram(texto)
        'Olá \\*mundo\\* com \\_ênfase\\_!'
    """
    
    # Caracteres que precisam ser escapados em Telegram MarkdownV2
    caracteres_especiais = [
        '_',  # underscore
        '*',  # asterisco
        '[',  # colchete aberto
        ']',  # colchete fechado
        '(',  # parêntese aberto
        ')',  # parêntese fechado
        '~',  # til
        '`',  # backtick
        '>',  # maior que
        '#',  # hashtag
        '+',  # mais
        '-',  # menos
        '=',  # igual
        '|',  # pipe
        '{',  # chave aberta
        '}',  # chave fechada
        '.',  # ponto
        '!',  # exclamação
    ]
    
    resultado = texto
    for char in caracteres_especiais:
        resultado = resultado.replace(char, f'\\{char}')
    
    return resultado


def truncar_historico(historico: List[Dict], max_mensagens: int = 20) -> List[Dict]:
    """
    Limita o histórico a um número máximo de mensagens.
    
    Remove mensagens antigas mantendo apenas as mais recentes.
    Útil para gerenciar memória e contexto de conversa.
    
    Args:
        historico (list): Lista de dicionários com mensagens
                         Formato: [{"role": "user"|"model", "conteudo": "...", "timestamp": "..."}, ...]
        max_mensagens (int): Número máximo de mensagens a manter. Padrão: 20
    
    Returns:
        list: Histórico limitado às últimas max_mensagens
    
    Exemplo:
        >>> historico = [{"role": "user", "conteudo": f"msg{i}", ...} for i in range(50)]
        >>> novo = truncar_historico(historico, max=20)
        >>> len(novo)
        20
    """
    
    if len(historico) <= max_mensagens:
        return historico
    
    # Mantém apenas as últimas max_mensagens
    return historico[-max_mensagens:]


def estimar_custo(tokens_entrada: int, tokens_saida: int) -> str:
    """
    Estima o custo de uso da Gemini API ou indica se está no tier gratuito.
    
    Gemini 1.5 Flash:
    - Tier Gratuito: Até 15 requisições por minuto (RPM) e 1M tokens/dia
    - Pago: Após exceder os limites gratuitos
    
    Esta função verifica se o uso acumulado ultrapassa os limites e retorna
    uma string informativa.
    
    Args:
        tokens_entrada (int): Número de tokens de entrada
        tokens_saida (int): Número de tokens de saída
    
    Returns:
        str: String indicando status de custo (gratuito ou estimativa)
    
    Exemplo:
        >>> estimar_custo(100, 50)
        'Gratuito (Tier Free) - 150 tokens consumidos'
        
        >>> estimar_custo(900_000, 200_000)
        'Gratuito (Tier Free) - Uso próximo ao limite: 1,100,000 / 1,000,000 tokens'
    """
    
    # Limites do Tier Gratuito Gemini 1.5 Flash
    LIMITE_DIARIO_TOKENS = 1_000_000  # 1M tokens por dia
    LIMITE_RPM = 15  # 15 requisições por minuto
    
    total_tokens = tokens_entrada + tokens_saida
    
    # Calcula o percentual de uso
    percentual_uso = (total_tokens / LIMITE_DIARIO_TOKENS) * 100
    
    # Monta a resposta
    if total_tokens < LIMITE_DIARIO_TOKENS:
        # Ainda dentro do limite gratuito
        tokens_restantes = LIMITE_DIARIO_TOKENS - total_tokens
        
        if percentual_uso > 80:
            # Aviso: Proxímo do limite
            return (
                f"Gratuito (Tier Free) ⚠️ - "
                f"Uso: {total_tokens:,} / {LIMITE_DIARIO_TOKENS:,} tokens "
                f"({percentual_uso:.1f}% utilizado)"
            )
        else:
            # Confortável dentro do limite
            return (
                f"Gratuito (Tier Free) ✅ - "
                f"Uso: {total_tokens:,} tokens "
                f"({tokens_restantes:,} restantes)"
            )
    else:
        # Excedeu o limite gratuito
        tokens_excedentes = total_tokens - LIMITE_DIARIO_TOKENS
        
        # Preço do Gemini 1.5 Flash (exemplo)
        # Entrada: $0.075 por 1M tokens
        # Saída: $0.30 por 1M tokens
        preco_entrada_por_milhao = 0.075
        preco_saida_por_milhao = 0.30
        
        custo_entrada = (tokens_entrada / 1_000_000) * preco_entrada_por_milhao
        custo_saida = (tokens_saida / 1_000_000) * preco_saida_por_milhao
        custo_total = custo_entrada + custo_saida
        
        return (
            f"Nível Pago - "
            f"Excedente: {tokens_excedentes:,} tokens - "
            f"Custo estimado: ${custo_total:.4f} USD"
        )


# ============================================================================
# TESTES RÁPIDOS (Opcional)
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 Testes do Módulo Formatador")
    print("="*70 + "\n")
    
    # Teste 1: Formatar para Telegram
    print("1️⃣ Teste: formatar_resposta_telegram()")
    texto_original = "Olá *mundo* com _ênfase_ e `código`!"
    texto_formatado = formatar_resposta_telegram(texto_original)
    print(f"   Original:   {texto_original}")
    print(f"   Formatado:  {texto_formatado}\n")
    
    # Teste 2: Truncar histórico
    print("2️⃣ Teste: truncar_historico()")
    historico_grande = [
        {"role": f"user" if i % 2 == 0 else "model", "conteudo": f"msg {i}"}
        for i in range(50)
    ]
    historico_truncado = truncar_historico(historico_grande, max_mensagens=10)
    print(f"   Histórico original: {len(historico_grande)} mensagens")
    print(f"   Histórico truncado: {len(historico_truncado)} mensagens")
    print(f"   Primeiras 3: {[h['conteudo'] for h in historico_truncado[:3]]}\n")
    
    # Teste 3: Estimar custo (dentro do limite)
    print("3️⃣ Teste: estimar_custo() - Dentro do limite")
    custo = estimar_custo(50_000, 30_000)
    print(f"   {custo}\n")
    
    # Teste 4: Estimar custo (próximo do limite)
    print("4️⃣ Teste: estimar_custo() - Próximo do limite")
    custo = estimar_custo(850_000, 100_000)
    print(f"   {custo}\n")
    
    # Teste 5: Estimar custo (excedente)
    print("5️⃣ Teste: estimar_custo() - Excedente")
    custo = estimar_custo(700_000, 500_000)
    print(f"   {custo}\n")
    
    print("="*70)
    print("✅ Todos os testes concluídos!")
    print("="*70)
