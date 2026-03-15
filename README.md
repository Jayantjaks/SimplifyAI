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

| Layer                | Technology              | Purpose                         |
| -------------------- | ----------------------- | ------------------------------- |
| **Backend**          | FastAPI                 | REST API server                 |
| **AI Orchestration** | LangGraph               | Multi-step AI workflow          |
| **AI Framework**     | LangChain               | LLM integration                 |
| **AI Model**         | Google Gemini 1.5 Flash | Text understanding & generation |
| **PDF Reading**      | PyMuPDF                 | Extract text from PDF           |
| **DOCX Reading**     | python-docx             | Extract text from Word files    |
| **Image OCR**        | Tesseract + Pillow      | Read text from scanned images   |
| **Database**         | SQLite + SQLAlchemy     | Store documents and results     |
| **Frontend**         | Streamlit               | Simple web UI                   |

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

### 2. Get a Free Google Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **Create API Key**
4. Copy the key

### 3. Configure Environment Variables

```bash
cd backend
cp .env.example .env
```

Open `.env` and paste your key:

```
GOOGLE_API_KEY=paste_your_key_here
```

### 4. Install Backend Dependencies

> Requires Python 3.11 or higher.

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate

pip install -r requirements.txt
```

> **Note for Windows users:** Tesseract OCR must be installed separately.
> Download from: https://github.com/UB-Mannheim/tesseract/wiki
> After installing, add it to your PATH or set the path in your code.

### 5. Install Frontend Dependencies

```bash
cd frontend
pip install -r requirements.txt
```

---

## Running the App

### Step 1 — Start the Backend API

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Visit **http://localhost:8000/docs** to see all API endpoints with a live test interface.

### Step 2 — Start the Frontend

Open a **new terminal**:

```bash
cd frontend
streamlit run app.py
```

The browser will open automatically at **http://localhost:8501**

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

## Using OpenAI Instead of Google Gemini

If you prefer OpenAI, update your `.env` file:

```
AI_PROVIDER=openai
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-4o-mini
```

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
→ Make sure `uvicorn` is running in a separate terminal on port 8000.

**"No text could be extracted"**
→ The PDF may be scanned/image-based. Try exporting a page as PNG and uploading the image instead.

**Tesseract not found (OCR error)**
→ Install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki (Windows) or `brew install tesseract` (Mac).

**AI API errors**
→ Check your `GOOGLE_API_KEY` in `.env`. Make sure it has access to the Gemini API.

---

## License

MIT — free to use, modify, and distribute.
