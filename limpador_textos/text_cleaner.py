import pandas as pd
import re
import string
from nltk.corpus import stopwords

# 1. Carregar os Dados
df = pd.read_csv('limpador_textos/dados_brutos.csv')
print("--- Dados Originais ---")
print(df)
print("\n")

# Lista de Stopwords em Português
stopwords_portugues = set(stopwords.words('portuguese'))
stopwords_extras = {'tá', 'tão', 'mas', 'muito', 'mais', 'já', 'ainda', 'só', 'se', 'meu', 'minha', 'teu', 'tua'}

stopwords_portugues_set = set(stopwords_portugues)
stopwords_extras_set = set(stopwords_extras)


def remover_pontuacao(texto):
    return texto.translate(str.maketrans('', '', string.punctuation))

def limpar_texto(texto):
    # 1. Converter para Minúsculas
    texto = texto.lower()

    # Remover Números (Nova linha do Desafio 1)
    # texto = re.sub(r'\d+', '', texto)

    # 2. Remover Pontuação (Usando a nova função com string.punctuation)
    texto = remover_pontuacao(texto) # Chamando a nova função auxiliar

    # 3. Remover números
    texto = re.sub(r'\d+', '', texto)  

    # 4. Remover Espaços em Excesso (múltiplos espaços)
    texto = re.sub(r'\s+', ' ', texto).strip()

    # 5. Remover Stopwords (Palavras Comuns)
    palavras = texto.split()
    palavras_filtradas = [palavra for palavra in palavras if palavra not in stopwords_portugues_set|stopwords_extras_set]
    texto_limpo = ' '.join(palavras_filtradas)

    return texto_limpo

# Aplicar a função de limpeza na coluna 'texto_bruto' e criar uma nova coluna
df['texto_limpo'] = df['texto_bruto'].apply(limpar_texto)

# Imprimir os Resultados
print("--- Dados Após a Limpeza ---")
print(df[['texto_bruto', 'texto_limpo']])

# Opcional: Salvar o resultado em um novo CSV
# df.to_csv('dados_limpos.csv', index=False)