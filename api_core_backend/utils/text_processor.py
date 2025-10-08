import re
import string
import nltk
import json
from nltk.corpus import stopwords
from pathlib import Path

# --- Verificação dos recursos NLTK ---
try:
    stopwords.words('portuguese')
except LookupError:
    print("INFO: Baixando pacote 'stopwords' do NLTK de forma segura...")
    nltk.download('stopwords')


class TextCleaner:
    def __init__(self):
        # Stopwords padrão
        self.stopwords_portugues = set(stopwords.words('portuguese'))

        # Carrega stopwords personalizadas do JSON
        config_path = Path(__file__).resolve().parents[2] / "config" / "stopwords_extras.json"
        if config_path.exists():
            with open(config_path, encoding="utf-8") as f:
                self.stopwords_extras = set(json.load(f))
        else:
            print("⚠️ Aviso: Arquivo stopwords_extras.json não encontrado. Usando conjunto básico.")
            self.stopwords_extras = set()

        # União de todos os sets
        self.stop_words_final = self.stopwords_portugues | self.stopwords_extras

    def _remover_pontuacao(self, texto):
        return texto.translate(str.maketrans('', '', string.punctuation))

    def clean(self, texto):
        texto = texto.lower()
        texto = self._remover_pontuacao(texto)
        texto = re.sub(r'\d+', '', texto)
        texto = re.sub(r'\s+', ' ', texto).strip()
        palavras = texto.split()
        palavras_filtradas = [p for p in palavras if p not in self.stop_words_final]
        return ' '.join(palavras_filtradas)
