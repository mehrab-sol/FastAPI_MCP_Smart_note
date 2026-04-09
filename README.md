# 🧠 Smart Notepad — FastAPI + PostgreSQL + MCP + LangGraph

A production-grade AI-powered notepad where you can talk to an LLM agent to save, read, search, and delete notes. Built with FastAPI, PostgreSQL, SQLAlchemy, MCP (Model Context Protocol), and LangGraph ReAct agent.

---

## 🏗️ Architecture

```
Browser / HTML UI
        ↓
   FastAPI REST API  ←→  /agent endpoint (LLM)
        ↓                        ↓
  SQLAlchemy ORM          MCP Server (stdio)
        ↓                        ↓
   PostgreSQL DB         MCP Tools (add, get, search, delete)
```

Two types of clients can use the app:
- A **human** hits REST endpoints directly (Swagger UI / HTML frontend)
- An **AI agent** uses MCP tools via natural language chat

---

## 📁 Project Structure

```
smart_notepad_v2/
│
├── app/
│   ├── __init__.py        ← makes app a Python package
│   ├── database.py        ← async PostgreSQL connection + session factory
│   ├── models.py          ← SQLAlchemy Note table model
│   ├── schemas.py         ← Pydantic request/response shapes
│   └── main.py            ← FastAPI app, REST endpoints, /agent endpoint
│
├── mcp_server.py          ← MCP server with 4 tools (wraps FastAPI)
├── client.py              ← Terminal LLM agent client
├── .env                   ← API key + database URL (never commit this)
└── requirements.txt       ← all Python dependencies
```

---

## ⚙️ Tech Stack

| Technology | Purpose |
|---|---|
| **FastAPI** | REST API framework |
| **PostgreSQL** | Production database |
| **SQLAlchemy (async)** | ORM — Python to SQL |
| **MCP (FastMCP)** | AI tool protocol server |
| **LangGraph** | ReAct agent framework |
| **LangChain OpenAI** | LLM connector |
| **httpx** | Async HTTP client inside MCP tools |
| **Pydantic** | Data validation |
| **python-dotenv** | Environment variable loader |

---

## 🚀 Setup & Installation

### 1. Clone the project and create a virtual environment

```bash
git clone <your-repo-url>
cd smart_notepad_v2
python3 -m venv .env_venv
source .env_venv/bin/activate
```

### 2. Install dependencies

```bash
pip install fastapi uvicorn sqlalchemy asyncpg psycopg2-binary python-dotenv \
            langchain-openai langchain-mcp-adapters langgraph mcp httpx
```

### 3. Setup PostgreSQL

```bash
sudo service postgresql start
sudo -u postgres psql
```

Inside postgres shell:

```sql
CREATE DATABASE smart_notepad;
CREATE USER notepad_user WITH PASSWORD 'notepad123';
GRANT ALL PRIVILEGES ON DATABASE smart_notepad TO notepad_user;
\c smart_notepad
GRANT ALL ON SCHEMA public TO notepad_user;
ALTER SCHEMA public OWNER TO notepad_user;
\q
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
DATABASE_URL=postgresql+asyncpg://notepad_user:notepad123@localhost/smart_notepad
```

---

## ▶️ Running the App

You need **two terminals open at the same time**.

**Terminal 1 — Start FastAPI:**

```bash
uvicorn app.main:app --reload
```

FastAPI will be available at: `http://127.0.0.1:8000`

**Terminal 2 — Run the terminal agent client (optional):**

```bash
python3 client.py
```

---

## 🌐 REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/notes` | Create a new note |
| `GET` | `/notes` | Get all notes |
| `GET` | `/notes/search?q=keyword` | Search notes by keyword |
| `DELETE` | `/notes/{title}` | Delete a note by title |
| `POST` | `/agent` | Send a message to the LLM agent |

### Interactive API docs (Swagger UI):

```
http://127.0.0.1:8000/docs
```

---

## 🤖 MCP Tools

The MCP server exposes 4 tools that the LLM agent can call:

| Tool | Description |
|---|---|
| `add_note(title, content)` | Saves a new note via POST /notes |
| `get_notes()` | Reads all notes via GET /notes |
| `search_note(query)` | Searches notes via GET /notes/search |
| `delete_note(title)` | Deletes a note via DELETE /notes/{title} |

---

## 🖥️ HTML Frontend

An HTML/JS frontend is included. Open the `.html` file in your browser while FastAPI is running.

**Features:**
- 💬 Chat window — talk to the LLM agent
- 📝 Notes panel — see all saved notes in real time
- 🔍 Live search bar in the sidebar
- 🗑️ One-click delete buttons
- 🟢 Server status indicator (auto-checks every 10 seconds)

---

## 🗄️ Database Schema

```sql
CREATE TABLE notes (
    id          SERIAL PRIMARY KEY,
    title       VARCHAR(255) UNIQUE NOT NULL,
    content     TEXT NOT NULL,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

---

## 📝 Example Usage

### Via terminal agent:

```
You: Save a note titled "Python" with content "Python is awesome"
Agent: Note 'Python' saved successfully!

You: Show me all my notes
Agent: 1. Python: Python is awesome

You: Search for notes about Python
Agent: Found 1 note — Python: Python is awesome

You: Delete the note titled Python
Agent: Note 'Python' deleted successfully!
```

### Via Swagger UI:

Go to `http://127.0.0.1:8000/docs` and use the interactive interface to test all endpoints.

---

## ⚠️ Known Limitations

- The free LLM model (`minimax/minimax-m2.5:free`) is rate-limited. If you get a 429 error, wait 1-2 minutes and retry.
- The `/agent` endpoint starts a new MCP server process per request — suitable for development, not high-traffic production.
- Note titles must be unique in the database.

---

## 🔮 Future Improvements

- Add user authentication (JWT)
- Deploy with Docker + docker-compose
- Switch to persistent MCP server connection (SSE transport)
- Add note update (PUT) endpoint
- Add pagination for large note collections

---

## 📄 License

MIT License — free to use and modify.
