# AI Compliance Agent

A **production-ready FastAPI service** that analyzes documents (PDF, DOCX, DOC) for English writing compliance, generates detailed reports, and automatically corrects violations using AI-powered rewriting with an **agentic orchestration workflow**.

## 🎯 Overview

The AI Compliance Agent provides a dual-mode system:

1. **Traditional Request-Response Flow**: Upload → Analyze → Download corrected document
2. **Agentic Autonomous Workflow**: Submit a compliance goal → Agent autonomously plans, extracts, rewrites, and delivers results with transparent job tracking

### Key Capabilities

- ✅ **Secure Document Upload** — PDF, DOCX, DOC with validation and size limits
- ✅ **Grammar & Style Analysis** — LanguageTool + AI-powered summaries via Mistral
- ✅ **Autonomous Agent Mode** — Submit high-level goals; agent runs background jobs with progress tracking
- ✅ **Job Orchestration** — Transparent job state, logs, and status polling via REST API
- ✅ **AI-Powered Rewriting** — Uses Mistral AI with fallback endpoints, retry logic, and rate-limit handling
- ✅ **Auto-Corrected Documents** — DOCX output with complete corrections applied
- ✅ **Interactive Swagger UI** — Full API documentation and test interface at `/docs`
- ✅ **Resilient Design** — Exponential backoff, circuit-breaker patterns, comprehensive logging
- ✅ **Secret Management** — Pre-commit secret detection, `.gitignore` safety, `.env` isolation

---

## 🤖 Agentic Workflow (New)

### What is the Agent?

The **SimpleAgentOrchestrator** is a background job runner that:
1. Accepts a high-level **compliance goal** (e.g., "Make document concise and professional")
2. Autonomously **extracts** document text
3. Calls the LLM **planner** to break down the goal into steps
4. **Applies corrections** using the LLM rewriter
5. **Persists job state** (JSON files) with timestamped logs
6. Returns a **fixed document** ready for download

### Job Lifecycle

```
User submits goal
        ↓
POST /agent/jobs { doc_id, goal }
        ↓
Job created in "queued" state
        ↓
Background thread starts
        ↓
[RUNNING] Extract → Plan → Rewrite
        ↓
[COMPLETED] Fixed doc saved & logs persisted
        ↓
User polls GET /agent/jobs/{job_id}
        ↓
Status = "completed"; download via GET /download/fixed/{doc_id}
```

### Job States

| State | Meaning |
|-------|---------|
| `queued` | Job created, waiting to run |
| `running` | Background thread is executing steps |
| `completed` | Job finished successfully; fixed doc ready |
| `failed` | Job encountered error; see logs for details |

---

## 🛠️ Tech Stack

- **Framework**: FastAPI (async-ready, OpenAPI/Swagger built-in)
- **Server**: Uvicorn with hot-reload support
- **AI Model**: Mistral AI (`open-mistral-7b` preferred; `mistral-medium` configurable)
- **Grammar Checking**: LanguageTool (local + public API fallback)
- **Document Processing**: pdfplumber, python-docx
- **HTTP Client**: httpx (with retry/backoff logic)
- **Environment**: python-dotenv (secure `.env` handling)
- **Testing**: pytest, pytest-asyncio
- **Security**: detect-secrets, pre-commit hooks

---

## 📋 Prerequisites

- **Python 3.9+**
- **Mistral API key** (free tier: [mistral.ai](https://mistral.ai))
- **Windows/macOS/Linux** (PowerShell, bash, or zsh)
- Optional: **Poppler** for PDF text rendering (auto-detects; OCR fallback available)

---

## 🚀 Installation

### 1. Clone & Navigate

```bash
git clone https://github.com/yourusername/ai-compliance-agent.git
cd ai-compliance-agent
```

### 2. Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy the example and add your Mistral API key:

```bash
cp .env.example .env
```

Edit `.env`:
```env
API_KEY=
MISTRAL_API_KEY=your_mistral_api_key_here
UPLOAD_DIR=./static
MAX_FILE_SIZE_BYTES=20971520
LANGUAGE_TOOL_LANG=en-US
```

**Get your Mistral API Key:**
1. Visit [console.mistral.ai](https://console.mistral.ai)
2. Sign up and create an API key
3. Paste it into `.env`

### 5. Start the Server

```bash
python -m uvicorn app.main:app --reload --log-level debug
```

Server runs at: **http://127.0.0.1:8000**

---

## 📚 API Documentation

### Interactive Endpoints

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **OpenAPI Schema**: http://127.0.0.1:8000/openapi.json

### Core Endpoints

#### Traditional Flow (Request-Response)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/upload/` | POST | Upload document for analysis |
| `/report/{doc_id}` | GET | Get compliance report (issues + summary) |
| `/fix/{doc_id}` | POST | Generate corrected document |
| `/download/original/{doc_id}` | GET | Download original document |
| `/download/fixed/{doc_id}` | GET | Download corrected document |
| `/health/` | GET | Health check / monitoring |

#### Agentic Flow (Job-Based)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/agent/jobs` | POST | Create a new agent job with goal |
| `/agent/jobs` | GET | List all jobs (recent) |
| `/agent/jobs/{job_id}` | GET | Get job status and logs |

---

## 💡 Usage Examples

### Traditional Flow (Swagger UI)

#### Step 1: Upload Document

1. Open http://127.0.0.1:8000/docs
2. Expand **POST /upload/**
3. Click "Try it out"
4. Choose a PDF or DOCX file
5. Click "Execute"
6. Note the returned `doc_id`

#### Step 2: Get Compliance Report

1. Expand **GET /report/{doc_id}**
2. Enter the `doc_id` from step 1
3. Click "Execute"
4. Review issues and AI summary

Example response:
```json
{
  "doc_id": "d0e66df0-8ec8-471b-92fe-c047460c2997",
  "issues": [
    {
      "line": 1,
      "message": "Possible typo: 'occured' → 'occurred'",
      "type": "TYPO"
    }
  ],
  "summary": "Document contains 3 grammar issues and 2 clarity suggestions."
}
```

#### Step 3: Apply Corrections

1. Expand **POST /fix/{doc_id}**
2. Enter the `doc_id`
3. Click "Execute"
4. Returns corrected text

#### Step 4: Download Fixed Document

1. Expand **GET /download/fixed/{doc_id}**
2. Enter the `doc_id`
3. Click "Execute"
4. Save as `fixed_document.docx`

### Agentic Flow (Job-Based Workflow)

#### Step 1: Upload Document

Same as traditional flow (Step 1 above).

#### Step 2: Create Agent Job

**Swagger UI:**
1. Expand **POST /agent/jobs**
2. Click "Try it out"
3. Enter JSON body:
```json
{
  "doc_id": "d0e66df0-8ec8-471b-92fe-c047460c2997",
  "goal": "Make the document concise, professional, and remove all passive voice constructions."
}
```
4. Click "Execute"
5. Note the returned `job_id`

**PowerShell:**
```powershell
$body = @{
  doc_id = "d0e66df0-8ec8-471b-92fe-c047460c2997"
  goal = "Make the document concise, professional, and remove all passive voice constructions."
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/agent/jobs" `
  -Method Post `
  -Body $body `
  -ContentType "application/json"
```

Expected response:
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

#### Step 3: Poll Job Status

**Swagger UI:**
1. Expand **GET /agent/jobs/{job_id}**
2. Enter the `job_id` from step 2
3. Click "Execute" multiple times to see progress

**PowerShell (Poll every 5 seconds):**
```powershell
$job_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

do {
  $status = Invoke-RestMethod -Uri "http://127.0.0.1:8000/agent/jobs/$job_id" -Method Get
  Write-Host "Status: $($status.status)"
  Write-Host "Logs: $($status.logs | ConvertTo-Json -Compress)"
  
  if ($status.status -in @("completed", "failed")) {
    Write-Host "Job finished!"
    break
  }
  
  Start-Sleep -Seconds 5
} while ($true)
```

Example job response (running):
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "doc_id": "d0e66df0-8ec8-471b-92fe-c047460c2997",
  "goal": "Make the document concise and professional.",
  "status": "running",
  "logs": [
    {
      "ts": 1731839400.123,
      "msg": "Extracting text from document"
    },
    {
      "ts": 1731839402.456,
      "msg": "Requesting plan from model"
    },
    {
      "ts": 1731839405.789,
      "msg": "Planner output: Step 1: Remove redundant phrases. Step 2: Convert passive voice..."
    }
  ]
}
```

#### Step 4: Download Corrected Document

When `status` == `"completed"`:

**Swagger UI:**
1. Expand **GET /download/fixed/{doc_id}**
2. Enter the original `doc_id`
3. Click "Execute"
4. Save as `fixed_document.docx`

**PowerShell:**
```powershell
$doc_id = "d0e66df0-8ec8-471b-92fe-c047460c2997"
Invoke-RestMethod -Uri "http://127.0.0.1:8000/download/fixed/$doc_id" `
  -Method Get `
  -OutFile "fixed_document.docx"
```

---

## 📊 Job Persistence & Logs

Job metadata and logs are persisted as JSON files for inspection and audit:

```
static/
  _jobs/
    a1b2c3d4-e5f6-7890-abcd-ef1234567890.json  ← Job state + logs
    b2c3d4e5-f6a7-8901-bcde-f12345678901.json
  d0e66df0-8ec8-471b-92fe-c047460c2997/
    original_doc.pdf                           ← Uploaded file
    fixed_d0e66df0-8ec8-471b-92fe-c047460c2997.docx  ← Corrected output
```

### Sample Job File

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "doc_id": "d0e66df0-8ec8-471b-92fe-c047460c2997",
  "goal": "Make the document concise and professional.",
  "status": "completed",
  "logs": [
    {
      "ts": 1731839400.123,
      "msg": "Extracting text from document"
    },
    {
      "ts": 1731839402.456,
      "msg": "Requesting plan from model"
    },
    {
      "ts": 1731839405.789,
      "msg": "Planner output: Step 1: Remove redundant phrases..."
    },
    {
      "ts": 1731839410.012,
      "msg": "Applying corrections based on goal"
    },
    {
      "ts": 1731839415.345,
      "msg": "Fixed document saved: fixed_d0e66df0-8ec8-471b-92fe-c047460c2997.docx"
    },
    {
      "ts": 1731839415.678,
      "msg": "Job completed successfully"
    }
  ]
}
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MISTRAL_API_KEY` | (required) | Mistral API key from console.mistral.ai |
| `MISTRAL_BASE_URL` | `https://api.mistral.ai` | Mistral API base URL |
| `UPLOAD_DIR` | `./static` | Where to store uploaded & corrected docs |
| `MAX_FILE_SIZE_BYTES` | `20971520` (20 MB) | Max upload file size |
| `LANGUAGE_TOOL_LANG` | `en-US` | Language for grammar checking |

### Adjusting Model & Parameters

Edit `app/services/rewrite_service.py` to change the default model or temperature:

```python
def rewrite_text(text: str) -> str:
    prompt = "..."
    corrected = generate_text(
        prompt,
        model="open-mistral-7b",  # Change model here
        max_tokens=2000,
        temperature=0.0  # 0 = deterministic, 1.0 = creative
    )
    return corrected
```

---

## 🧪 Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ --cov=app --cov-report=html
```

Open `htmlcov/index.html` in your browser for coverage details.

---

## 🔒 Security & Best Practices

### Secrets Management

- ✅ `.env` is in `.gitignore` — never committed
- ✅ Pre-commit hook detects secrets before push
- ✅ Use `.env.example` as a template (no real keys)
- ✅ Rotate keys regularly if exposed

### Pre-Commit Setup

Install and configure pre-commit to catch secrets:

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

### CORS & Authentication

The API currently allows all origins for development. In production:

1. Edit `app/main.py` to restrict CORS origins:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

2. Add Bearer token authentication to protected endpoints.

3. Use HTTPS (e.g., behind a reverse proxy like Nginx).

---

## 🏗️ Architecture

### Project Structure

```
ai-compliance-agent/
├── app/
│   ├── api/
│   │   ├── upload.py          # File upload endpoint
│   │   ├── report.py          # Compliance report endpoint
│   │   ├── fix.py             # Rewrite endpoint
│   │   ├── download.py        # Download endpoint
│   │   ├── agent.py           # Agent job endpoints (NEW)
│   │   └── health.py          # Health check
│   ├── services/
│   │   ├── extraction_service.py     # PDF/DOCX text extraction
│   │   ├── compliance_service.py     # Grammar checks + summaries
│   │   ├── rewrite_service.py        # LLM rewriting
│   │   ├── mistral_client.py         # Mistral HTTP client with retries
│   │   ├── storage_service.py        # File storage & validation
│   │   └── agent_orchestrator.py     # Job orchestration (NEW)
│   ├── models/
│   │   ├── upload_models.py
│   │   ├── report_models.py
│   │   └── fix_models.py
│   ├── utils/
│   │   ├── file_validation.py
│   │   ├── ocr_utils.py
│   │   └── security.py
│   ├── main.py                # FastAPI app
│   ├── config.py              # Configuration
│   └── dependencies.py        # Dependency injection
├── tests/
│   ├── test_api.py
│   └── sample_docs/
├── static/                    # Uploaded files & job state
│   ├── _jobs/                 # Job metadata (JSON)
│   └── {doc_id}/              # Per-document folders
├── .env.example               # Environment template
├── .env                       # Local secrets (gitignore'd)
├── .gitignore
├── .pre-commit-config.yaml
├── .secrets.baseline          # Detect-secrets baseline
├── requirements.txt
├── README.md
└── docker-compose.yml
```

### Service Layer Design

```
HTTP Request
    ↓
Router (api/*.py)
    ↓
Service Layer:
    ├── extraction_service.py → extract text
    ├── compliance_service.py → analyze issues
    ├── rewrite_service.py    → call LLM
    ├── mistral_client.py     → HTTP client (retry/fallback)
    ├── storage_service.py    → file I/O
    └── agent_orchestrator.py → job management (NEW)
    ↓
Response / Background Job
```

---

## 🚨 Error Handling & Resilience

### Mistral API Retry Logic

The `mistral_client.py` automatically:
- Retries on `429 (Rate Limited)` and `5xx` errors
- Uses exponential backoff with jitter
- Falls back from `/v1/models/{model}/generate` to `/v1/chat/completions`
- Logs all attempts and final status

### Job Failure Handling

If a job fails:
- Status is set to `"failed"`
- Error message logged in job JSON
- User can inspect logs via `GET /agent/jobs/{job_id}`
- Original document remains unchanged

---

## 📈 Performance Tips

### Large Documents

- Documents > 5 MB may take longer to process
- Text extraction scales linearly with file size
- LLM processing time depends on token count

### Rate Limiting

- Mistral free tier: ~30 requests/minute
- Agent orchestrator queues jobs (runs one per thread)
- Multiple concurrent jobs may exceed rate limits (see logs for backoff messages)

### Scaling (Future)

For production scaling, consider:
- **Job Queue**: Replace threads with Celery + Redis
- **Caching**: Add Redis for LLM response caching
- **Database**: Persist jobs to PostgreSQL/MongoDB instead of JSON files
- **Load Balancer**: Deploy multiple Uvicorn workers behind Nginx/HAProxy

---

## 🐳 Docker Deployment

Build and run with Docker:

```bash
docker build -t ai-compliance-agent .
docker run -p 8000:8000 -e MISTRAL_API_KEY=your_key ai-compliance-agent
```

Or use docker-compose:

```bash
docker-compose up -d
```

---

## 📝 Logging & Debugging

Enable debug logging:

```bash
python -m uvicorn app.main:app --log-level debug
```

Log output includes:
- HTTP request/response details
- Mistral API calls and retries
- Job lifecycle events
- File I/O operations

For agent jobs, full step-by-step logs are persisted in `static/_jobs/{job_id}.json`.

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit changes (`git commit -am 'Add my feature'`)
4. Push to branch (`git push origin feature/my-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see `LICENSE` file for details.

---

## 🆘 Troubleshooting

### "Mistral API key not configured"

**Solution:** Ensure `.env` has `MISTRAL_API_KEY=<your_key>` and restart the server.

```bash
# Verify key is loaded:
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Key present:', bool(os.getenv('MISTRAL_API_KEY')))"
```

### "429 Too Many Requests" errors

**Solution:** You've hit Mistral rate limits. The client auto-retries; check logs for backoff messages. For production, upgrade your Mistral plan or implement request throttling.

### "File too large" on upload

**Solution:** Increase `MAX_FILE_SIZE_BYTES` in `.env` (default 20 MB).

### "ModuleNotFoundError: No module named 'pdf2image'"

**Solution:** Install optional OCR dependencies:
```bash
pip install pdf2image pytesseract
```

### Job status stuck on "running"

**Solution:** Check server logs for exceptions. If the LLM call hangs, restart the server. Job files are persisted; you can inspect them manually at `static/_jobs/{job_id}.json`.

---

## 📞 Support

For issues, questions, or feature requests:

- **GitHub Issues**: [Create an issue](https://github.com/yourusername/ai-compliance-agent/issues)
- **Email**: support@yourdomain.com
- **Documentation**: See `/docs` (Swagger UI) for API details

---

## 🎉 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) — Modern web framework
- [Mistral AI](https://mistral.ai/) — LLM provider
- [LanguageTool](https://languagetool.org/) — Grammar checking
- [pdfplumber](https://github.com/jsvine/pdfplumber) — PDF extraction
- [python-docx](https://python-docx.readthedocs.io/) — DOCX handling

---


