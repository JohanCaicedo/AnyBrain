import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chainlit as cl
from openai import OpenAI
from src.config import DB_PATH, EMBEDDING_MODEL_NAME, LLM_API_KEY
from src.core.database import VectorDatabase
from chainlit.input_widget import Select, TextInput
import edge_tts
import re

# --- INICIALIZACIÓN ---
db = VectorDatabase(DB_PATH, EMBEDDING_MODEL_NAME)

def clean_text_for_audio(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'#+\s?', '', text)
    text = re.sub(r'```[\s\S]*?```', ' código ', text)
    return text

def get_llm_client(provider, api_key_input=None):
    """Configura el cliente según el proveedor elegido"""
    key = api_key_input if api_key_input and api_key_input.strip() else LLM_API_KEY

    if provider == "Google Gemini":
        return OpenAI(api_key=key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
    elif provider == "Ollama (Local)":
        return OpenAI(api_key="ollama", base_url="http://localhost:11434/v1")
    elif provider == "DeepSeek":
        return OpenAI(api_key=key, base_url="https://api.deepseek.com")
    elif provider == "OpenAI (ChatGPT)":
        return OpenAI(api_key=key, base_url="https://api.openai.com/v1")
    return None

async def dibujar_ajustes(proveedor_actual):
    """
    Menú de configuración de AnyBrain
    """
    inputs = [
        Select(
            id="Provider",
            label="🧠 Proveedor de IA",
            values=["Google Gemini", "Ollama (Local)", "DeepSeek", "OpenAI (ChatGPT)"],
            initial_index=["Google Gemini", "Ollama (Local)", "DeepSeek", "OpenAI (ChatGPT)"].index(proveedor_actual)
        ),
        TextInput(
            id="SystemPrompt", 
            label="🎭 Personalidad", 
            initial="Eres AnyBrain, un asistente experto, directo y técnico."
        )
    ]

    if proveedor_actual == "Google Gemini":
        inputs.extend([
            Select(
                id="ModelName",
                label="💎 Modelo Google",
                values=["gemini-1.5-pro-latest", "gemini-1.5-flash", "gemini-2.0-flash-exp"],
                initial_index=0
            ),
            TextInput(id="ApiKey", label="🔑 Google API Key (Opcional)", initial="")
        ])

    elif proveedor_actual == "Ollama (Local)":
        inputs.extend([
            TextInput(id="ModelName", label="🦙 Modelo Ollama (Ej: llama3)", initial="llama3.1")
        ])

    elif proveedor_actual == "DeepSeek":
        inputs.extend([
            TextInput(id="ModelName", label="🤖 Modelo DeepSeek", initial="deepseek-chat"),
            TextInput(id="ApiKey", label="🔑 DeepSeek API Key", initial="")
        ])

    elif proveedor_actual == "OpenAI (ChatGPT)":
        inputs.extend([
            Select(
                id="ModelName",
                label="🧠 Modelo GPT",
                values=["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
                initial_index=0
            ),
            TextInput(id="ApiKey", label="🔑 OpenAI API Key", initial="")
        ])

    await cl.ChatSettings(inputs).send()

@cl.on_chat_start
async def start():
    # Por defecto arrancamos con Google
    provider_default = "Google Gemini"
    
    await dibujar_ajustes(provider_default)

    cl.user_session.set("client", get_llm_client(provider_default))
    cl.user_session.set("model_name", "gemini-1.5-pro-latest")
    cl.user_session.set("system_prompt", "Eres AnyBrain, un asistente experto.")
    cl.user_session.set("current_provider", provider_default)

    # MENSAJE DE BIENVENIDA ACTUALIZADO
    await cl.Message(content="🧠 **AnyBrain Listo**\n\nSistema de embeddings cargado. Abre los Ajustes (⚙️) para configurar tu modelo de IA.").send()

@cl.on_settings_update
async def setup_agent(settings):
    nuevo_proveedor = settings["Provider"]
    proveedor_anterior = cl.user_session.get("current_provider")

    if nuevo_proveedor != proveedor_anterior:
        cl.user_session.set("current_provider", nuevo_proveedor)
        await dibujar_ajustes(nuevo_proveedor)
        await cl.Message(content=f"🔄 **AnyBrain cambiando a {nuevo_proveedor}...**\nAbre Ajustes de nuevo para finalizar.").send()
        return

    model = settings.get("ModelName", "gemini-1.5-pro-latest")
    api_key = settings.get("ApiKey", "")
    prompt = settings["SystemPrompt"]

    new_client = get_llm_client(nuevo_proveedor, api_key)
    
    cl.user_session.set("client", new_client)
    cl.user_session.set("model_name", model)
    cl.user_session.set("system_prompt", prompt)

    await cl.Message(content=f"✅ **AnyBrain Configurado**\n\n- Motor: {nuevo_proveedor}\n- Modelo: `{model}`").send()

@cl.on_message
async def main(message: cl.Message):
    client = cl.user_session.get("client")
    model = cl.user_session.get("model_name")
    system_instruction = cl.user_session.get("system_prompt")

    # 1. RAG
    docs = db.similarity_search(message.content, k=5)
    context_str = "\n\n".join([f"[Fuente: {d.metadata.get('source', 'unk')}]\n{d.page_content}" for d in docs])
    
    # 2. Generación
    try:
        stream = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": f"CONTEXTO:\n{context_str}\n\nCONSULTA:\n{message.content}"}
            ],
            stream=True
        )
        
        msg = cl.Message(content="")
        full_text = ""
        
        for chunk in stream:
            token = chunk.choices[0].delta.content
            if token:
                await msg.stream_token(token)
                full_text += token
                
        await msg.update()
        
        # 3. Voz
        actions = [cl.Action(name="voice", payload={"text": full_text}, label="🔊 Escuchar", description="TTS")]
        msg.actions = actions
        await msg.update()

    except Exception as e:
        await cl.Message(content=f"❌ **Error en AnyBrain:** {str(e)}").send()

@cl.action_callback("voice")
async def voice_action(action):
    text = clean_text_for_audio(action.payload["text"])
    await cl.Message(content="🗣️ Generando audio...").send()
    comm = edge_tts.Communicate(text, "es-CO-GonzaloNeural")
    await comm.save("temp.mp3")
    await cl.Message(content="", elements=[cl.Audio(name="Audio", path="temp.mp3", display="inline")]).send()