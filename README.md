# ✈️ Wanderlust AI — Local Travel Planning Web App

An intelligent, 100% local travel planning web application powered by **Ollama**, **FastAPI**, and a **PostgreSQL** database. Type your dream trip in plain English or use the interactive trip builder form to automatically receive a realistic, comprehensive travel itinerary with flights, boutique hotels, weather/packing tips, day-by-day pacing, and rough budget breakdowns.

---

## 🌟 Key Features

- **🗣️ Natural Language Trip Generation**: Type a trip in plain English (e.g. *"A 5-day cultural trip to Florence & Tuscany in May focusing on food, wine, and renaissance art"*).
- **🎛️ Interactive Trip Builder**: Structured form for travelers who don't want to type sentences (destination, departure, duration, budget tier, travel styles, group composition, and special interests).
- **🧠 100% Free & Local AI (Ollama)**: Uses your local Ollama models (`llama3.2:latest`, `llama3.1:latest`, `llama3.2:1b`, or `qwen2.5:3b`). No paid APIs, zero recurring costs.
- **🐘 Native PostgreSQL Database**: Automatically stores and indexes all itineraries and chat history in a local PostgreSQL 18 database with seamless SQLite fallback.
- **💬 Conversational Follow-Up Q&A**: Reopen any saved trip from the sidebar and ask follow-up questions (*"What if it rains on Day 2?"*, *"Suggest 3 authentic dinner spots"*, *"How do I get around cheaply?"*) without starting over.
- **📋 Export Options**:
  - **Copy Plan**: One-click copy formatted Markdown to clipboard.
  - **Download Markdown**: Download clean `.md` itinerary file.
  - **Print / PDF**: Dedicated `@media print` styling that formats the itinerary into an elegant printable travel booklet.
- **🎨 Modern Polished UI**:
  - Light & Dark mode toggle (persists to localStorage).
  - Collapsible sidebar with saved trips, real-time search, and deletion.
  - Live status pills for Ollama and PostgreSQL with latency metrics.
  - Dynamic model selector populated directly from installed Ollama models.
- **🇩🇪 Germany & Privacy Safe**: Zero torrents, zero illegal downloads, no external telemetry or tracking. Operates strictly on `localhost` complying fully with GDPR.

---

## 🚀 Quick Start

### 1. Requirements
- **Python 3.10+** (Python 3.14 supported)
- **Ollama** installed with models (e.g. `llama3.2:latest`, `llama3.1:latest`, etc.)
- **PostgreSQL 18** (already installed locally)

### 2. Launch the Application

Run the all-in-one launcher script:

```powershell
.\run.ps1
```

Or double-click **`run.bat`**.

This script will:
1. Verify and start the local PostgreSQL 18 cluster on port 5432.
2. Confirm Ollama is running at `http://127.0.0.1:11434`.
3. Start the FastAPI server at `http://127.0.0.1:8000`.
4. Open your default web browser to the application interface.

---

## 📁 Project Architecture

```
d:\Projects\ai-travel-planner\
├── .venv\                  # Python virtual environment
├── app\
│   ├── __init__.py
│   ├── config.py           # Configuration & environment variables
│   ├── database.py         # SQLAlchemy engine (PostgreSQL + SQLite fallback)
│   ├── export_utils.py     # Markdown & text export formatters
│   ├── main.py             # FastAPI REST endpoints & static routes
│   ├── models.py           # SQLAlchemy Trip & ChatMessage models
│   ├── ollama_client.py    # Async Ollama REST client
│   ├── planner.py          # Prompt engineering & JSON parsing engine
│   └── schemas.py          # Pydantic data schemas
├── data\
│   └── pgdata\             # Dedicated PostgreSQL database cluster
├── scripts\
│   ├── start_db.ps1        # Script to start PostgreSQL
│   └── stop_db.ps1         # Script to stop PostgreSQL
├── static\
│   ├── css\styles.css      # Custom styling & print CSS
│   ├── js\app.js           # Client-side SPA application logic
│   └── index.html          # Responsive single page application
├── .env                    # Active environment settings
├── .env.example            # Environment template
├── requirements.txt        # Python package dependencies
├── run.ps1                 # PowerShell launcher
└── run.bat                 # Windows shortcut launcher
```

---

## 📡 REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Live status & latency of Ollama and PostgreSQL |
| `GET` | `/api/models` | List of installed Ollama models |
| `GET` | `/api/trips` | List all saved trips (ordered newest first) |
| `POST` | `/api/trips/generate` | Generate trip from plain English or form inputs |
| `GET` | `/api/trips/{trip_id}` | Retrieve full trip details with chat history |
| `DELETE` | `/api/trips/{trip_id}` | Delete trip and associated conversations |
| `POST` | `/api/trips/{trip_id}/chat` | Ask follow-up question regarding a trip |
| `GET` | `/api/trips/{trip_id}/export/markdown` | Download trip plan as `.md` file |

---

## 🛡️ Privacy & Compliance Notice

- All AI inference executes locally on your GPU/CPU via Ollama at `127.0.0.1:11434`.
- No travel queries or personal information leave your machine.
- All database records are stored in your local PostgreSQL instance at `127.0.0.1:5432`.
