# Assistente Pessoal com IA (FastAPI + Gemini + NLP)

Assistente virtual desenvolvido em **Python** e **FastAPI** com interface web integrada. O projeto combina roteamento automático de intenções (*skills*), pré-processamento de linguagem natural (NLP com `NLTK`) e integração com o **Google Gemini** para conversação contextual, resumo, tradução e análise de texto.

---

## Funcionalidades

- **Roteamento Automático de Skills (`skills.py`):** identifica a intenção da mensagem e direciona para módulos específicos:
  - Resumo estruturado de textos em tópicos;
  - Tradução multi-idioma;
  - Análise e revisão textual;
  - Geração de listas estruturadas;
  - Limpeza de texto (remoção de *stopwords* customizáveis e pontuação via `NLTK`);
  - Conversão de unidades de temperatura via linguagem natural.
- **Memória Conversacional (`gemini_brain.py`):** gerenciamento de sessões com histórico multi-turn (até 20 mensagens por sessão) e contabilização de tokens de entrada e saída.
- **Interface Web Integrada:** frontend leve em HTML, CSS e JavaScript para interação direta com a API.

---

## Estrutura do Projeto

```text
assistente-pessoal-ia/
├── api_core_backend/
│   ├── api_conversor.py       # Servidor FastAPI e definição de rotas
│   ├── gemini_brain.py        # Gerenciamento de sessão, histórico e integração Gemini
│   ├── skills.py              # Detecção de intenção e funções especializadas
│   └── utils/
│       ├── formatador.py      # Padronização de respostas
│       └── text_processor.py  # Limpeza de texto e stopwords (NLTK)
├── config/
│   └── stopwords_extras.json  # Lista customizável de stopwords adicionais
├── frontend_conversor/
│   └── index.html             # Interface web do chat
├── test_assistant.py          # Testes automatizados da aplicação
├── requirements.txt           # Dependências Python
└── .env.example               # Template de variáveis de ambiente
```

---

## Configuração e Execução Local

### 1. Ambiente Virtual e Dependências

```bash
# Criar e ativar ambiente virtual (Windows PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements.txt

# Baixar base de stopwords do NLTK
python -c "import nltk; nltk.download('stopwords')"
```

### 2. Variáveis de Ambiente

Copie `.env.example` para `.env` e informe sua chave de API do Google Gemini:

```env
GEMINI_API_KEY=sua_chave_aqui
```

### 3. Iniciar o Backend

```bash
uvicorn api_core_backend.api_conversor:app --reload
```

O servidor ficará disponível em `http://127.0.0.1:8000`. Para utilizar a interface visual, abra o arquivo `frontend_conversor/index.html` no navegador.

---

## Endpoints Principais

- **`POST /chat`** — Processa mensagens com detecção automática de *skill* e memória de sessão (`session_id`).
- **`GET /chat/historico`** — Retorna o histórico de mensagens da sessão ativa.
- **`GET /chat/stats`** — Exibe métricas de uso da sessão (total de mensagens e tokens consumidos).
- **`POST /chat/limpar`** — Reinicia o contexto da sessão.
- **`POST /processar-texto`** e **`POST /converter-temperatura`** — Rotas dedicadas para limpeza de texto e conversão direta.
- **`GET /health`** — Verificação de status da API.

---

## Tecnologias Utilizadas

- **Python 3.11+**
- **FastAPI** & **Uvicorn**
- **Google Generative AI (Gemini)**
- **NLTK (Natural Language Toolkit)**
- **HTML5 / CSS3 / JavaScript**

---

## Autor e Licença

- **Autor:** [Ariston Gomes](https://www.linkedin.com/in/ariston-gomes/)
- **Licença:** Distribuído sob a licença MIT.
