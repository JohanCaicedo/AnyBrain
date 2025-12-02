import os
from dotenv import load_dotenv

load_dotenv()

# --- RUTAS ABSOLUTAS ---
# Calculamos la ruta base independientemente de dónde se ejecute el script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Rutas de Datos
DATA_DIR = os.path.join(BASE_DIR, "data")
INPUTS_PATH = os.path.join(DATA_DIR, "inputs")
DB_PATH = os.path.join(DATA_DIR, "vector_db")
HISTORY_PATH = os.path.join(DATA_DIR, "history")
REGISTRY_PATH = os.path.join(DATA_DIR, "registry.txt")

# --- CONFIGURACIÓN DE MODELOS ---
# Modelo de Embeddings (Local y Potente)
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Configuración del LLM (Por defecto Google, pero cambiable)
LLM_PROVIDER = "GOOGLE"  # Opciones: GOOGLE, OLLAMA, DEEPSEEK
LLM_API_KEY = os.getenv("LLM_API_KEY", "") # Pon tu clave en un archivo .env o pégala aquí si prefieres
LLM_MODEL_NAME = "gemini-1.5-pro-latest" # O el que prefieras