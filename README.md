# 🤖 Assistente Pessoal com IA (NLP + FastAPI)

Um projeto de **Assistente Pessoal Inteligente** desenvolvido em **Python (FastAPI)** com um **frontend integrado**, capaz de processar texto em linguagem natural e realizar ações simples, como **limpeza de texto** e **conversão de temperatura**.

---

## ✨ Funcionalidades Atuais

- 🧹 **Limpeza de texto (NLP)** – remove stopwords, pontuação e palavras irrelevantes.  
- 🌡️ **Conversão de temperatura** – interpreta comandos como “converter 72F para Celsius”.  
- 💬 **Interface web integrada** – chat simples e responsivo em HTML/CSS/JS.  
- ⚙️ **Arquitetura modular** – separação entre backend, frontend e utilitários.  
- 🧠 **Stopwords personalizáveis** – carregadas dinamicamente via arquivo JSON.  

---

## 📂 Estrutura do Projeto

```
assistente-pessoal-ia/
│
├── api_core_backend/
│  ├── api_conversor.py # Backend principal (FastAPI)
│  └── utils/
│  └── text_processor.py # Limpeza e pré-processamento de texto
│
├── config/
│  └── stopwords_extras.json # Lista de stopwords personalizadas
│
├── frontend_conversor/
│  └── index.html # Interface do chat
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Como Rodar o Projeto (Localmente)

Siga os passos abaixo na raiz do projeto (`assistente-pessoal-ia/`):

### 1. Configuração do Ambiente

   **Ative o ambiente virtual:**
   ```bash
   .\venv\Scripts\Activate.ps1
   ```
   **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```
   **Baixe os recursos NLP (stopwords):**
   ```bash
   python -c "import nltk; nltk.download('stopwords')"
   ```
---

### 2. Iniciar o Backend

Abra um terminal e mantenho o rodando:

'''uvicorn api_core_backend.api_conversor:app --reload'''

Servidor disponível em:
👉 http://127.0.0.1:8000

---

### 3. Abrir a Interface

Abra o arquivo frontend_conversor/index.html diretamente no navegador.

## 🧠 Exemplo de Uso

Digite no chat:

“limpe esta frase: o produto é muito bom, só que 10 vezes mais caro!”

Resposta esperada:

Entendido! O texto limpo é: 'limpar frase produto bom vezes caro'

---

## 🧩 Tecnologias Utilizadas

Python 3.11+

FastAPI

Uvicorn

NLTK

HTML / CSS / JavaScript

## 👨‍💻 Autor

Ariston Gomes

Entusiasta de tecnologia, IA e desenvolvimento de software.

## 📝 Licença

Este projeto está sob a licença MIT.
Sinta-se à vontade para usar, modificar e compartilhar.

---
