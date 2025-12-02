# 🧠 AnyBrain

**AnyBrain** is an open-source, local RAG (Retrieval-Augmented Generation) tool designed to effortlessly create and query embeddings from your personal documents. Turn any folder of files into an intelligent, queryable brain using the power of LLMs.

## ✨ Features

- **Universal Ingestion:** Automatically processes multiple formats:
  - 📄 **PDF** (Digital & Scanned via GPU-accelerated OCR)
  - 📝 **Word** (`.docx`) & Text (`.txt`, `.md`)
  - 📊 **Excel** (`.xlsx`)
  - 🖼️ **Images** (`.jpg`, `.png`) containing text.
- **Model Agnostic:** Seamlessly switch between **Ollama (Local)**, **Google Gemini**, **DeepSeek**, or **OpenAI**.
- **Privacy First:** Vector processing and storage happen locally on your machine using **ChromaDB**.
- **Modern Interface:** Built with Chainlit, featuring Neural Text-to-Speech (TTS) and dynamic settings.

## 🚀 Quick Start

No complex setup required. AnyBrain handles the environment for you.

1. **Clone the repository** (or download as ZIP).
2. **Add your files** to the `data/inputs` folder.
3. **Double-click `start.bat`**.

The script will automatically:
- Check for Python.
- Create a virtual environment (`venv`).
- Install all dependencies (CUDA enabled).
- Ingest your documents.
- Launch the Chat Interface in your browser.

## 🛠️ Configuration

Once the interface is running, click on the **Settings (⚙️)** icon to:
- Switch AI Providers (Local vs Cloud).
- Enter API Keys (stored securely in session).
- Change the assistant's personality.

## 📦 Requirements

- **OS:** Windows (Batch script provided).
- **Python:** 3.10 or higher.
- **GPU (Optional):** NVIDIA GPU recommended for faster OCR and Embedding generation.

## 📂 Project Structure

```text
AnyBrain/
├── data/
│   ├── inputs/          # Drop your files here
│   ├── vector_db/       # Local Knowledge Base (Chroma)
│   └── history/         # Saved chat sessions
├── src/                 # Source code
├── start.bat            # Auto-installer & Launcher
└── requirements.txt     # Python dependencies