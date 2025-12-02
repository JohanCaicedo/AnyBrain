import os
from dotenv import load_dotenv

# Esto carga las claves del archivo .env automáticamente
load_dotenv()

# --- RUTAS ABSOLUTAS ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")
INPUTS_PATH = os.path.join(DATA_DIR, "inputs")
DB_PATH = os.path.join(DATA_DIR, "vector_db")
HISTORY_PATH = os.path.join(DATA_DIR, "history")
REGISTRY_PATH = os.path.join(DATA_DIR, "registry.txt")

# --- CONFIGURACIÓN DE MODELOS ---
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

LLM_PROVIDER = "GOOGLE"

# --- ¡SEGURIDAD! ---
# Ya no ponemos la clave aquí. Le decimos que la busque en el entorno.
# Si no la encuentra, se queda vacía (y la pedirá en el chat).
LLM_API_KEY = os.getenv("LLM_API_KEY", "") 

LLM_MODEL_NAME = "gemini-1.5-pro"