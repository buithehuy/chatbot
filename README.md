# 🤖 Modular RAG-Enabled Chatbot Agent

A modular, extensible AI chatbot with **tool-calling** and **Retrieval-Augmented Generation (RAG)** capabilities. Supports multiple LLM backends (Gemini, OpenAI, Groq) via a unified interface, enabling seamless switching between providers.

---

## ✨ Features

- 🔄 **Multi-LLM Support** — Plug-and-play backends: Google Gemini, OpenAI GPT, Groq (LLaMA)
- 🛠️ **Tool-Calling Agent Loop** — Parallel function calling with up to 5 agentic reasoning steps
- 📚 **RAG Pipeline** — Indexes local text files, embeds with `sentence-transformers`, stores in ChromaDB
- 🔌 **Extensible Tool System** — Registry-based tool management; add new tools without touching core logic
- 🔒 **Secure Calculator** — AST-based arithmetic evaluation (no `eval()`)
- 🌦️ **Live Weather** — Real-time data via OpenWeatherMap API
- 💾 **Persistent Vector Store** — ChromaDB persists embeddings across sessions; deduplication built-in

---

## 🏗️ Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         User Input                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                      ChatBot (chatbot.py)                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │           Agentic Reasoning Loop (max 5 steps)        │  │
│  │  ┌──────────┐   tool calls?   ┌──────────────────┐   │  │
│  │  │  Model   │ ──────────────► │  Tool Executor   │   │  │
│  │  │  .chat() │ ◄────────────── │  (tool results)  │   │  │
│  │  └──────────┘   no more calls └──────────────────┘   │  │
│  └───────────────────────────────────────────────────────┘  │
│                            │                                │
│                   Final response                            │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
                 User Output
```

### Component Diagram

```
chatbot/
│
├── main.py                   # Entry point — wires everything together
├── chatbot.py                # Core agent loop logic
├── config.py                 # Settings (model names, system prompt)
├── messages.py               # Message / AssistantMessage dataclasses
├── responses.py              # ChatResponse / ToolCall dataclasses
│
├── models/                   # LLM Backends (all implement BaseModel)
│   ├── base.py               # Abstract BaseModel interface
│   ├── gemini_model.py       # Google Gemini (google-genai)
│   ├── openai_model.py       # OpenAI GPT (openai)
│   └── groq_model.py         # Groq LLaMA (groq) — with tool_use_failed fallback
│
├── tools/                    # Tool ecosystem
│   ├── base.py               # Abstract BaseTool interface
│   ├── tool.py               # Tool dataclass
│   ├── tool_registry.py      # Registry — register / get tools by name
│   ├── tool_executor.py      # Dispatches tool calls safely
│   ├── calculator.py         # AST-safe arithmetic evaluator
│   ├── weather.py            # OpenWeatherMap live weather
│   └── knowledge_base.py     # RAG retrieval tool (wraps Retriever)
│
├── rag/                      # Retrieval-Augmented Generation pipeline
│   ├── chunker.py            # Sentence-boundary text chunking with overlap
│   ├── embedder.py           # SentenceTransformer embeddings (all-MiniLM-L6-v2)
│   ├── vector_store.py       # ChromaDB persistent vector store
│   └── retriever.py          # Indexes files; queries top-k chunks
│
├── chroma_db/                # Persisted vector store (auto-created)
├── knowledge.txt             # Default knowledge base document
└── .env                      # API keys (not committed)
```

### Agent Tool-Calling Flow

```
User: "What's the weather in Hanoi and who is Nguyen Van A?"
        │
        ▼
  ChatBot.chat()
        │
        ├──► Model.chat(history)
        │         │
        │    returns tool_calls:
        │    [weather("Hanoi"), knowledge_base("Nguyen Van A")]
        │
        ├──► ToolExecutor.execute(weather)      → JSON weather data
        ├──► ToolExecutor.execute(knowledge_base) → retrieved chunks
        │
        ├──► Append tool results to history
        │
        ├──► Model.chat(history + tool results)
        │         │
        │    returns final text answer
        │
        └──► Return answer to user
```

### RAG Pipeline

```
index_file("knowledge.txt")
        │
        ▼
  Read raw text
        │
        ▼
  chunker.chunk_text()          ← sentence-boundary chunking
  (chunk_size=500, overlap=100)
        │
        ▼
  Embedder.embed_batch()        ← all-MiniLM-L6-v2 (384-dim)
        │
        ▼
  VectorStore.add()             ← ChromaDB (persistent)
        │
        ▼
  ✅ Indexed & deduplicated

At query time:
  knowledge_base.execute(query)
        │
        ▼
  Embedder.embed(query)
        │
        ▼
  VectorStore.search(top_k=3)   ← cosine similarity
        │
        ▼
  Return top-3 chunks to LLM
```

---

## 🚀 Quick Start

### 1. Clone & install dependencies

```bash
git clone <your-repo-url>
cd chatbot

python -m venv .venv
source .venv/bin/activate

pip install google-genai openai groq sentence-transformers chromadb python-dotenv requests
```

### 2. Configure API keys

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
GROQ_API_KEY=your_groq_api_key
OPENWEATHER_API_KEY=your_openweathermap_api_key
```

### 3. Add your knowledge base

Edit `knowledge.txt` with any content you want the bot to know about. The file is indexed automatically on first run.

### 4. Run

```bash
python main.py
```

```
You: What's the weather in Tokyo and what is 15 * 8?
⚙ Tool call: weather  args={'city': 'Tokyo'}
⚙ Tool result: {...}
⚙ Tool call: calculator  args={'expression': '15*8'}
⚙ Tool result: 120
Bot: The weather in Tokyo is 22°C and partly cloudy. 15 × 8 = 120.
```

---

## 🔧 Switching LLM Backend

In `main.py`, comment/uncomment the model you want:

```python
# model = geminimodel   # Google Gemini 2.5 Flash
# model = openaimodel   # OpenAI GPT-4o
model = groqmodel       # Groq LLaMA 3.3 70B (default)
```

| Backend | Model | Notes |
|---------|-------|-------|
| Gemini  | `gemini-2.5-flash` | Uses Google GenAI SDK; FunctionDeclaration format |
| OpenAI  | `gpt-4o` | Standard OpenAI tool-calling |
| Groq    | `llama-3.3-70b-versatile` | Auto-retries without tools on `tool_use_failed` |

---

## 🛠️ Adding a Custom Tool

1. Create a file in `tools/`, subclass `BaseTool`:

```python
# tools/my_tool.py
from tools.base import BaseTool

class MyTool(BaseTool):
    @property
    def name(self): return "my_tool"

    @property
    def description(self): return "Does something useful."

    def execute(self, param: str) -> str:
        return f"Result for {param}"

    def to_schema(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "param": {"type": "string", "description": "Input parameter"}
                    },
                    "required": ["param"]
                }
            }
        }
```

2. Register it in `main.py`:

```python
from tools.my_tool import MyTool
registry.register(MyTool())
```

That's it — the agent will automatically use it when appropriate.

---

## 📦 Project Dependencies

| Package | Purpose |
|---------|---------|
| `google-genai` | Gemini LLM backend |
| `openai` | OpenAI GPT backend |
| `groq` | Groq LLaMA backend |
| `sentence-transformers` | Text embeddings for RAG |
| `chromadb` | Persistent vector store |
| `python-dotenv` | Load `.env` API keys |
| `requests` | HTTP calls (weather API) |

---

## 📁 Key Design Decisions

- **Unified message format** — All models normalize their messages to/from the internal `Message` / `AssistantMessage` dataclasses, keeping `ChatBot` provider-agnostic.
- **Raw tool call preservation** — Each model stores raw tool call formats in history so multi-turn conversations replay correctly with the same provider.
- **AST-safe calculator** — Uses Python's `ast` module with an allowlist of operators instead of `eval()` to prevent code injection.
- **Idempotent indexing** — `Retriever.index_file()` checks ChromaDB metadata before indexing to prevent duplicate chunks across restarts.
- **Groq resilience** — Automatically retries failed requests without tools when Groq returns `tool_use_failed`, ensuring graceful degradation.

---

## 📄 License

MIT
