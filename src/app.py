import sys
import os
import json
import re
import asyncio
from openai import OpenAI

# Ajuste de rutas
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chainlit as cl
from src.config import DB_PATH, EMBEDDING_MODEL_NAME, DATA_DIR
from src.core.database import VectorDatabase
from chainlit.input_widget import Select, TextInput
import edge_tts

# --- CONFIGURACIÓN DE PERSISTENCIA ---
CONFIG_FILE = os.path.join(DATA_DIR, "user_config.json")

# --- INICIALIZACIÓN ---
db = VectorDatabase(DB_PATH, EMBEDDING_MODEL_NAME)

def load_user_config():
    """Carga la configuración guardada"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {}

def save_user_config(new_data):
    """Actualiza y guarda la configuración sin borrar lo anterior"""
    current_config = load_user_config()
    current_config.update(new_data)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(current_config, f, indent=4)

def clean_text_for_audio(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'#+\s?', '', text)
    text = re.sub(r'```[\s\S]*?```', ' código ', text)
    text = re.sub(r'\[.*?\]', '', text)
    return text

def get_client(provider, api_key=None):
    if provider == "Google Gemini":
        return OpenAI(api_key=api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
    elif provider == "Ollama (Local)":
        return OpenAI(api_key="ollama", base_url="http://localhost:11434/v1")
    elif provider == "DeepSeek":
        return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    elif provider == "OpenAI (ChatGPT)":
        return OpenAI(api_key=api_key, base_url="https://api.openai.com/v1")
    return None

async def update_settings_ui(provider, selected_model=None):
    """Construye el menú recuperando la clave guardada ESPECÍFICA de ese proveedor"""
    
    # 1. Recuperar clave guardada para este proveedor
    saved_config = load_user_config()
    saved_key = ""
    
    if provider == "Google Gemini":
        saved_key = saved_config.get("google_key", "")
    elif provider == "DeepSeek":
        saved_key = saved_config.get("deepseek_key", "")
    elif provider == "OpenAI (ChatGPT)":
        saved_key = saved_config.get("openai_key", "")

    inputs = [
        Select(
            id="Provider",
            label="🧠 Proveedor de IA",
            values=["Google Gemini", "Ollama (Local)", "DeepSeek", "OpenAI (ChatGPT)"],
            initial_index=["Google Gemini", "Ollama (Local)", "DeepSeek", "OpenAI (ChatGPT)"].index(provider)
        )
    ]

    # 2. Mostrar campo de clave (Pre-rellenado si ya existe)
    if provider != "Ollama (Local)":
        inputs.append(TextInput(id="ApiKey", label=f"🔑 API Key ({provider})", initial=saved_key))

    # 3. Mostrar campo de modelo
    default_model = selected_model or "gemini-1.5-flash"
    if provider == "Ollama (Local)": default_model = "llama3.1"
    
    inputs.append(TextInput(id="ModelName", label="💎 Modelo", initial=default_model))
    inputs.append(TextInput(id="SystemPrompt", label="🎭 Personalidad", initial="Eres AnyBrain, un asistente experto."))
    
    await cl.ChatSettings(inputs).send()

@cl.on_chat_start
async def start():
    saved_config = load_user_config()
    
    # Cargar último proveedor usado o Google por defecto
    provider = saved_config.get("last_provider", "Google Gemini")
    model = saved_config.get("last_model", "gemini-1.5-flash")
    
    # Recuperar la clave correcta según el proveedor
    api_key = ""
    if provider == "Google Gemini": api_key = saved_config.get("google_key", "")
    elif provider == "DeepSeek": api_key = saved_config.get("deepseek_key", "")
    elif provider == "OpenAI (ChatGPT)": api_key = saved_config.get("openai_key", "")

    # Configurar sesión
    cl.user_session.set("provider", provider)
    cl.user_session.set("api_key", api_key)
    cl.user_session.set("model", model)
    cl.user_session.set("client", get_client(provider, api_key))
    cl.user_session.set("system_prompt", "Eres AnyBrain.")

    await update_settings_ui(provider, model)
    
    msg = f"🧠 **AnyBrain Listo**\nConectado a: **{provider}**\nModelo: `{model}`"
    if not api_key and provider != "Ollama (Local)":
        msg += "\n\n⚠️ **Falta API Key.** Ve a Ajustes (⚙️) para configurarla."
    
    await cl.Message(content=msg).send()

@cl.on_settings_update
async def setup_agent(settings):
    provider = settings["Provider"]
    api_key = settings.get("ApiKey", "")
    model = settings["ModelName"]
    prompt = settings["SystemPrompt"]

    # --- LÓGICA INTELIGENTE DE GUARDADO ---
    # Guardamos la clave en su casillero correspondiente
    config_to_save = {
        "last_provider": provider,
        "last_model": model
    }
    
    if api_key: # Solo guardamos si el usuario escribió algo
        if provider == "Google Gemini":
            config_to_save["google_key"] = api_key
        elif provider == "DeepSeek":
            config_to_save["deepseek_key"] = api_key
        elif provider == "OpenAI (ChatGPT)":
            config_to_save["openai_key"] = api_key

    save_user_config(config_to_save)
    # --------------------------------------

    # Si cambió el proveedor, intentamos cargar la clave guardada de ese nuevo proveedor
    # para que la sesión no se quede con la clave del anterior
    if not api_key:
        saved = load_user_config()
        if provider == "Google Gemini": api_key = saved.get("google_key", "")
        elif provider == "DeepSeek": api_key = saved.get("deepseek_key", "")
        elif provider == "OpenAI (ChatGPT)": api_key = saved.get("openai_key", "")

    cl.user_session.set("client", get_client(provider, api_key))
    cl.user_session.set("model", model)
    cl.user_session.set("system_prompt", prompt)
    cl.user_session.set("provider", provider)
    cl.user_session.set("api_key", api_key)

    # Refrescar menú para que muestre la clave correcta del nuevo proveedor
    await update_settings_ui(provider, model)

    await cl.Message(content=f"✅ **Configuración Guardada**\nProveedor: {provider}").send()

@cl.on_message
async def main(message: cl.Message):
    client = cl.user_session.get("client")
    model = cl.user_session.get("model")
    
    # Validación básica
    if not client or (not cl.user_session.get("api_key") and cl.user_session.get("provider") != "Ollama (Local)"):
        await cl.Message(content="❌ **Falta API Key.**\nVe a Ajustes (⚙️), selecciona tu proveedor y pon la clave.").send()
        return

    docs = db.similarity_search(message.content, k=4)
    source_elements = [cl.Text(name=f"Fuente {i+1}", content=d.page_content, display="side") for i, d in enumerate(docs)]
    context_str = "\n\n".join([f"[Fuente {i+1}]: {d.page_content}" for i, d in enumerate(docs)])

    try:
        stream = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": cl.user_session.get("system_prompt")},
                {"role": "user", "content": f"Contexto:\n{context_str}\n\nPregunta: {message.content}"}
            ],
            stream=True
        )
        
        msg = cl.Message(content="", elements=source_elements)
        full_text = ""
        
        for chunk in stream:
            token = chunk.choices[0].delta.content
            if token:
                await msg.stream_token(token)
                full_text += token
        
        await msg.update()
        
        actions = [cl.Action(name="voice", payload={"text": full_text}, label="🔊 Escuchar", description="TTS")]
        msg.actions = actions
        await msg.update()

    except Exception as e:
        await cl.Message(content=f"❌ **Error:** {str(e)}").send()

@cl.action_callback("voice")
async def voice_action(action):
    text = clean_text_for_audio(action.payload["text"])
    await cl.Message(content="🗣️ Generando audio...").send()
    comm = edge_tts.Communicate(text, "es-CO-GonzaloNeural")
    await comm.save("temp.mp3")
    await cl.Message(content="", elements=[cl.Audio(name="Audio", path="temp.mp3", display="inline")]).send()