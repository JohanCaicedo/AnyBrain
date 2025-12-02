import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from tqdm import tqdm
import torch

class VectorDatabase:
    def __init__(self, db_path, model_name):
        self.db_path = db_path
        
        # CONFIGURACIÓN GPU PARA EMBEDDINGS
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"      ⚡ Motor de Embeddings corriendo en: {device.upper()}")
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': device}
        )
        
        self.vector_store = Chroma(
            persist_directory=db_path,
            embedding_function=self.embeddings
        )
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=200
        )

    def add_documents(self, documents):
        """Recibe lista de objetos Document y los guarda con barra de progreso"""
        
        # 1. Cortar en fragmentos
        print("      ✂️  Fragmentando texto...")
        chunks = self.splitter.split_documents(documents)
        total_chunks = len(chunks)
        print(f"      🧩 Se generaron {total_chunks} fragmentos.")
        
        if total_chunks == 0:
            return

        # 2. Insertar en lotes para mostrar progreso
        BATCH_SIZE = 100 # Procesamos de 100 en 100
        
        print(f"      🧠 Generando vectores (Guardando en DB)...")
        for i in tqdm(range(0, total_chunks, BATCH_SIZE), desc="Vectorizando", unit="lote"):
            batch = chunks[i : i + BATCH_SIZE]
            self.vector_store.add_documents(batch)
            
    def similarity_search(self, query, k=5):
        return self.vector_store.similarity_search(query, k=k)