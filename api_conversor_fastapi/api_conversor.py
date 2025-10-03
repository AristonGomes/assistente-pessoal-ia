from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # << ADICIONAR ESTA LINHA

# 1. Cria a instância do FastAPI
app = FastAPI()

origins = [
    # O asterisco (*) permite qualquer origem. Para fins de desenvolvimento local, é seguro.
    # Em produção, você colocaria o endereço do seu site (ex: "https://meusite.com")
    "*" 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Permite as origens definidas acima
    allow_credentials=True,
    allow_methods=["*"], # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"], # Permite todos os headers
)

# 2. Define um endpoint (rota) de teste simples
# O decorador @app.get("/") mapeia esta função para a URL raiz
@app.get("/")
def home():
    """
    Endpoint principal para verificar se a API está ativa.
    """
    return {"message": "API de Conversão de Temperatura Ativa!"}

# 3. Define o endpoint de conversão
# Recebe a temperatura (temp_f) como um parâmetro de URL (query parameter)
@app.get("/converter")
def converter_fahrenheit_celsius(temp_f: float):
    """
    Converte uma temperatura de Fahrenheit (F°) para Celsius (C°).
    
    Este endpoint aceita um valor float 'temp_f' como parâmetro de consulta (query parameter).
    Exemplo: /converter?temp_f=68
    """
    # Fórmula de conversão: (F - 32) * 5/9
    temp_c = (temp_f - 32) * 5/9
    
    # Retorna o resultado como um objeto JSON
    return {
        "temperatura_fahrenheit": temp_f,
        "temperatura_celsius": round(temp_c, 2),
        "unidade": "C"
    }

# Para rodar: uvicorn api_conversor_fastapi.api_conversor:app --reload