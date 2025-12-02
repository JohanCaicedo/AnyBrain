import sys
import os
# Truco para que encuentre los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import INPUTS_PATH, DB_PATH, REGISTRY_PATH, EMBEDDING_MODEL_NAME
from src.core.processor import FileProcessor
from src.core.database import VectorDatabase
from langchain_core.documents import Document

def load_registry():
    if not os.path.exists(REGISTRY_PATH): return []
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines()]

def update_registry(filename):
    with open(REGISTRY_PATH, "a", encoding="utf-8") as f:
        f.write(f"{filename}\n")

def main():
    print("🚀 INICIANDO SISTEMA DE INGESTA (Modo Feedback Visual)")
    print(f"📂 Carpeta de Entrada: {INPUTS_PATH}")
    
    # 1. Detectar archivos nuevos
    if not os.path.exists(INPUTS_PATH):
        os.makedirs(INPUTS_PATH)
        print("⚠️ Carpeta inputs creada. Pon tus archivos ahí.")
        return

    all_files = os.listdir(INPUTS_PATH)
    processed_files = load_registry()
    new_files = [f for f in all_files if f not in processed_files and not f.startswith(".")]

    if not new_files:
        print("\n✅ Todo está actualizado. No hay archivos nuevos.")
        return

    print(f"\n📦 Se encontraron {len(new_files)} archivos nuevos.")
    
    # 2. Inicializar Motores
    processor = FileProcessor()
    # Inicializamos DB (Aquí verás si usa GPU)
    db = VectorDatabase(DB_PATH, EMBEDDING_MODEL_NAME)
    
    docs_to_ingest = []
    successful_files = []

    # 3. Procesar Archivos (Lectura + OCR)
    print("\n--- FASE 1: LECTURA Y OCR ---")
    for filename in new_files:
        print(f"   ▶️  Procesando: {filename}")
        file_path = os.path.join(INPUTS_PATH, filename)
        
        try:
            text = processor.process_file(file_path)
            
            if len(text) > 50:
                doc = Document(page_content=text, metadata={"source": filename})
                docs_to_ingest.append(doc)
                successful_files.append(filename)
            else:
                print(f"      ⚠️  Advertencia: Archivo vacío o ilegible.")
                
        except Exception as e:
            print(f"      ❌ Error: {e}")

    # 4. Vectorización (Embeddings)
    if docs_to_ingest:
        print("\n--- FASE 2: VECTORIZACIÓN E INDEXADO ---")
        db.add_documents(docs_to_ingest)
        
        # Actualizar registro
        for f in successful_files:
            update_registry(f)
            
        print(f"\n✨ ¡ÉXITO! {len(successful_files)} archivos añadidos al cerebro.")
    else:
        print("\n⚠️ No se pudo extraer texto válido de los archivos.")

if __name__ == "__main__":
    main()