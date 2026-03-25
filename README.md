# SimplifyAI — AI Legal & Medical Document Simplifier

> Upload any complex legal or medical document and get a **plain-English explanation** in seconds.

---

## What Is This?

Many people receive documents they cannot fully understand:

- Medical reports and prescriptions
- Legal agreements and contracts
- Insurance policies and claim forms

**SimplifyAI** solves this. You upload the document, and the AI:

1. Reads it
2. Rewrites it in simple language anyone can understand
3. Highlights the most important terms, risks, and key points
4. Gives you a short bullet-point summary
5. (Optional) Translates everything to Hindi

---

## How It Works — Step by Step

```
User uploads file (PDF / DOCX / Image)
          │
          ▼
   Text Extraction
   ├── PDF   → PyMuPDF
   ├── DOCX  → python-docx
   └── Image → Tesseract OCR
          │
          ▼
   AI Pipeline (LangGraph)
   ├── Step 1: Classify → "Is this medical, legal, or insurance?"
   ├── Step 2: Simplify → Rewrite in plain English
   ├── Step 3: Highlight → Extract terms, risks, key clauses
   ├── Step 4: Summarize → 5–8 bullet points
   └── Step 5: Translate → Hindi (only if requested)
          │
          ▼
   Results shown in Streamlit UI
   (also saved to SQLite database)
```

---

## Tech Stack

| Layer                | Technology                                    | Purpose                         |
| -------------------- | --------------------------------------------- | ------------------------------- |
| **Backend**          | FastAPI                                       | REST API server                 |
| **AI Orchestration** | LangGraph                                     | Multi-step AI workflow          |
| **AI Framework**     | LangChain                                     | LLM integration                 |
| **AI Model**         | Groq (Llama 3.3 70B) / Google Gemini / OpenAI | Text understanding & generation |
| **PDF Reading**      | PyMuPDF                                       | Extract text from PDF           |
| **DOCX Reading**     | python-docx                                   | Extract text from Word files    |
| **Image OCR**        | Tesseract + Pillow                            | Read text from scanned images   |
| **Database**         | SQLite + SQLAlchemy                           | Store documents and results     |
| **Frontend**         | Streamlit                                     | Simple web UI                   |

---

## Project Structure

```
Health-AI/
├── backend/
│   ├── app/
│   │   ├── main.py               ← FastAPI app entry point
│   │   ├── config.py             ← Settings (API keys, DB URL)
│   │   ├── database.py           ← Database setup
│   │   ├── models/
│   │   │   └── document.py       ← Database table definition
│   │   ├── schemas/
│   │   │   └── document.py       ← API request/response shapes
│   │   ├── routers/
│   │   │   └── document.py       ← API endpoints (upload, list, get, delete)
│   │   ├── services/
│   │   │   └── extraction.py     ← PDF / DOCX / OCR text extraction
│   │   └── core/
│   │       └── langgraph_flow.py ← The full AI pipeline (LangGraph)
│   ├── requirements.txt
│   └── .env.example              ← Copy this to .env and add your API key
│
├── frontend/
│   ├── app.py                    ← Streamlit web UI
│   └── requirements.txt
│
├── uploads/                      ← Temporary file storage (git-ignored)
└── README.md
```

---

## Setup Guide

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd Health-AI
```

### 2. Get an AI API Key

This project supports **three AI providers**. You only need one:

| Provider               | How to get a key                                                               | Default? |
| ---------------------- | ------------------------------------------------------------------------------ | -------- |
| **Groq** (recommended) | [console.groq.com](https://console.groq.com/) → API Keys → Create              | Yes      |
| Google Gemini          | [aistudio.google.com](https://aistudio.google.com/app/apikey) → Create API Key | No       |
| OpenAI                 | [platform.openai.com](https://platform.openai.com/api-keys) → Create Key       | No       |

### 3. Configure Environment Variables

```bash
cd backend
copy .env.example .env        # Windows
# cp .env.example .env         # Mac / Linux
```

Open `backend/.env` and fill in your API key:

```env
# ── Using Groq (default) ──
AI_PROVIDER=groq
GROQ_API_KEY=paste_your_groq_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# ── OR using Google Gemini ──
# AI_PROVIDER=google
# GOOGLE_API_KEY=paste_your_google_key_here
# GEMINI_MODEL=gemini-2.5-flash

# ── OR using OpenAI ──
# AI_PROVIDER=openai
# OPENAI_API_KEY=paste_your_openai_key_here
# OPENAI_MODEL=gpt-4o-mini

DATABASE_URL=sqlite:///./simplifyai.db
APP_NAME=SimplifyAI
DEBUG=false
MAX_UPLOAD_SIZE_MB=10
```

### 4. Set Up the Virtual Environment & Install Backend Dependencies

> Requires **Python 3.11 or higher**.

```bash
cd backend
```

**Create venv (first time only):**

```bash
python -m venv venv
```

**Activate the venv:**

```bash
# Windows (Command Prompt)
venv\Scripts\activate

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Mac / Linux
source venv/bin/activate
```

> After activation you should see `(venv)` at the beginning of your terminal prompt.

**Install dependencies:**

```bash
pip install -r requirements.txt
```

> **Note for Windows users (image OCR only):** Tesseract OCR must be installed separately if you want to upload images.
> Download from: https://github.com/UB-Mannheim/tesseract/wiki
> After installing, add it to your system PATH.

### 5. Install Frontend Dependencies

With the venv still activated:

```bash
pip install -r ../frontend/requirements.txt
```

Or from the project root:

```bash
pip install -r frontend/requirements.txt
```

---

## Running the App

> **Important:** Always activate the venv before running any command.

### Step 1 — Activate the Virtual Environment

```bash
cd backend

# Windows (Command Prompt)
venv\Scripts\activate

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Mac / Linux
source venv/bin/activate
```

### Step 2 — Start the Backend API

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

- **Swagger UI (test endpoints in browser):** http://localhost:8000/docs
- **Health check:** http://localhost:8000/health

### Step 3 — Start the Frontend

Open a **new terminal**, activate the venv again, then:

```bash
cd backend
venv\Scripts\activate          # Windows CMD
# .\venv\Scripts\Activate.ps1   # Windows PowerShell
# source venv/bin/activate       # Mac / Linux

cd ../frontend
streamlit run app.py
```

The browser will open automatically at **http://localhost:8501**

### Quick Start (Windows — both terminals)

**Terminal 1 — Backend:**

```cmd
cd Health-AI\backend
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**

```cmd
cd Health-AI\backend
venv\Scripts\activate
cd ..\frontend
streamlit run app.py
```

---

## Using the App

1. Go to **http://localhost:8501** in your browser
2. Click **Browse files** and upload a PDF, DOCX, or image
3. Choose output language (English or Hindi)
4. Click **Simplify Document**
5. Wait 15–30 seconds for AI processing
6. Read your results:
   - **Quick Summary** — 5–8 bullet points
   - **Key Highlights** — Important terms, risks, and key clauses
   - **Simplified Explanation** — Full plain-English version
   - **Hindi Translation** — If you selected Hindi

---

## API Endpoints

| Method   | Endpoint                 | Description                   |
| -------- | ------------------------ | ----------------------------- |
| `POST`   | `/api/v1/upload`         | Upload a file and process it  |
| `GET`    | `/api/v1/documents`      | List all processed documents  |
| `GET`    | `/api/v1/documents/{id}` | Get details for one document  |
| `DELETE` | `/api/v1/documents/{id}` | Delete a document             |
| `GET`    | `/health`                | Check if API is running       |
| `GET`    | `/docs`                  | Interactive API documentation |

### Example: Upload via curl

```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@/path/to/document.pdf" \
  -F "target_language=en"
```

---

## AI Pipeline Details

The AI pipeline is built with **LangGraph** — a framework for building multi-step AI workflows. Each step is a separate "node" in the graph:

```
classify → simplify → highlight → summarize → (translate if Hindi)
```

| Node          | What It Does                                               |
| ------------- | ---------------------------------------------------------- |
| **classify**  | Detects document type: medical, legal, insurance, or other |
| **simplify**  | Rewrites the document in plain, everyday English           |
| **highlight** | Extracts key terms, risks/warnings, and important clauses  |
| **summarize** | Creates a short bullet-point summary                       |
| **translate** | (Optional) Translates the result to Hindi                  |

---

## Switching AI Providers

Edit `backend/.env` and change `AI_PROVIDER` + the matching API key:

**Groq (default):**

```env
AI_PROVIDER=groq
GROQ_API_KEY=your_groq_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

**Google Gemini:**

```env
AI_PROVIDER=google
GOOGLE_API_KEY=your_google_key_here
GEMINI_MODEL=gemini-2.5-flash
```

**OpenAI:**

```env
AI_PROVIDER=openai
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-4o-mini
```

Restart the backend after changing the provider.

---

## Git Branch Structure

This project follows a feature-branch workflow:

| Branch                    | Purpose                                      |
| ------------------------- | -------------------------------------------- |
| `main`                    | Stable, production-ready code                |
| `feature/project-setup`   | Initial directory structure and config files |
| `feature/backend-core`    | FastAPI app, database, models, schemas       |
| `feature/text-extraction` | PDF, DOCX, and OCR text extraction           |
| `feature/ai-pipeline`     | LangGraph AI workflow                        |
| `feature/api-routes`      | REST API endpoints                           |
| `feature/streamlit-ui`    | Streamlit web interface                      |
| `docs/readme`             | Documentation                                |

---

## Troubleshooting

**"Cannot connect to the backend"**
→ Make sure the venv is activated and `uvicorn` is running in a separate terminal on port 8000.

**`ModuleNotFoundError` when starting the server**
→ You forgot to activate the venv. Run `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux) first.

**"No text could be extracted"**
→ The PDF may be scanned/image-based. Try exporting a page as PNG and uploading the image instead.

**Tesseract not found (OCR error)**
→ Install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki (Windows) or `brew install tesseract` (Mac).

**AI API errors**
→ Check your API key in `backend/.env`. Make sure `AI_PROVIDER` matches the key you provided (groq, google, or openai).

**PowerShell: "running scripts is disabled on this system"**
→ Run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` and try again.

---

## License

MIT — free to use, modify, and distribute.
