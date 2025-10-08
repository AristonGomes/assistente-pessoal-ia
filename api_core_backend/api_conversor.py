from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel # Para definir o formato da requisição POST
from api_core_backend.utils.text_processor import TextCleaner # << Importa nosso módulo de limpeza
import uvicorn
import re

# ----------------------------------------------------
# 1. Setup Básico
# ----------------------------------------------------
app = FastAPI()

nlp_cleaner: TextCleaner # Variável global para a ferramenta de NLP

# Configuração CORS (Permite que o Frontend se conecte)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Inicializa Ferramentas de NLP
# A classe TextCleaner é carregada na memória uma única vez

# Função de Inicialização (Executa APENAS quando o servidor inicia)
@app.on_event("startup")
async def startup_event():
    global nlp_cleaner
    print("INFO: Inicializando módulo TextCleaner...")
    # Inicializa a ferramenta APÓS o carregamento do ambiente
    nlp_cleaner = TextCleaner() 
    print("INFO: TextCleaner carregado com sucesso.")

# 3. Modelo Pydantic para a Requisição POST
# Define o contrato de dados: a API espera um JSON com a chave 'texto'
class UserInput(BaseModel):
    texto: str


# ----------------------------------------------------
# 4. Rota Inteligente (O Cérebro do Assistente)
# ----------------------------------------------------
@app.post("/assistente")
def handle_assistant_request(input_data: UserInput):
    """
    Endpoint principal do assistente. Recebe um texto e decide a ação.
    """
    texto_bruto = input_data.texto
    
    # --- Lógica de Intenção Rudimentar (Commit 3) ---
    
    # 1. Limpar e padronizar o texto para análise
    texto_limpo = nlp_cleaner.clean(texto_bruto)
    
    # 2. DECISÃO: Se o usuário quer apenas limpar o texto
    if "limpar" in texto_limpo:
        # Retorna o resultado da limpeza
        return {
            "status": "sucesso",
            "acao": "limpeza_texto",
            "resposta": f"Entendido! O texto limpo é: '{texto_limpo}'"
        }
    
    # 3. DECISÃO: Se o usuário quer converter temperatura
    elif "graus" in texto_limpo or "fahrenheit" in texto_limpo:
        # Tentativa de extrair o número (Lógica será aprimorada futuramente)
        try:
            # Pega o primeiro número que encontrar no texto original (assumindo que é o F°)
            temp_f = float(re.findall(r'\d+\.?\d*', texto_bruto)[0])
            
            # Fórmula de conversão: (F - 32) * 5/9
            temp_c = (temp_f - 32) * 5/9
            
            return {
                "status": "sucesso",
                "acao": "conversao_temperatura",
                "resposta": f"A temperatura de {temp_f}°F é igual a {round(temp_c, 2)}°C."
            }
        except:
            return {"status": "erro", "resposta": "Não consegui extrair a temperatura para conversão."}


    # 4. DECISÃO: Resposta padrão
    else:
        return {
            "status": "sucesso",
            "acao": "resposta_padrao",
            "resposta": f"Olá! Não entendi sua intenção, mas você disse: '{texto_bruto}'"
        }

# ----------------------------------------------------
# Rota de Teste e Conversão Antigas (REMOVIDAS/COMENTADAS para focar na rota /assistente)
# Opcionalmente, você pode deixar o @app.get("/") para fins de teste.
@app.get("/")
def home():
    """Endpoint principal para verificar se a API está ativa."""
    return {"message": "API do Assistente Pessoal Ativa (Use a rota /assistente POST)."}
# ----------------------------------------------------
