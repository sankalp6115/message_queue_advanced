# PyQueue

PyQueue is a lightweight, persistent background-job queue built with FastAPI, SQLite, and SQLAlchemy. It is designed for local development, experimentation, and learning the fundamental architecture behind distributed worker queues without needing external services like Redis, Celery, or RabbitMQ.

---

## Architecture & Data Flow

```text
┌──────────────────────┐         HTTP Enqueue         ┌─────────────────────────┐
│ Client / Web UI      │ ───────────────────────────> │    FastAPI Producer     │
│ (frontend/index.html)│                              │      (backend/api)      │
└──────────────────────┘                              └─────────────────────────┘
          ▲                                                        │
          │ Polling / Query Status                                 │ INSERT job (pending)
          │ GET /api/jobs/{id}                                     ▼
┌──────────────────────┐                              ┌─────────────────────────┐
│ Worker Process Pool  │ <──── Atomic Claim (running) ─────── │   SQLite jobs Table     │
│ (backend/workers)    │                                      │       (jobs.db)         │
└──────────────────────┘                                      └─────────────────────────┘
          │                                                        ▲
          ▼                                                        │
┌──────────────────────┐                                           │
│ Task Handlers        │ ────────── Commit Result / Status ────────┘
│ (sleep / calc / img) │            (completed / failed)
└──────────────────────┘
```

1. **Producer (FastAPI)**: Validates incoming payloads via Pydantic discriminators and persists a job record with `pending` status, returning a UUID immediately.
2. **Persistence (SQLite)**: Functions as the durable queue, tracking job states, timestamps, payloads, results, and error tracebacks.
3. **Consumer (Worker Pool)**: One or more independent background worker processes poll SQLite, atomically claim pending jobs (`status = 'running'`), execute the assigned handler, and record results or errors.
4. **Crash Recovery**: An automated sweeper periodically detects abandoned `running` jobs (e.g., from an unhandled worker crash) and requeues them back to `pending`.

---

## Supported Job Types

- **`image`**: Compresses uploaded images into multiple quality variants (`25%`, `50%`, `75%`, `90%`) using Pillow and saves results into `assets/output_images/`.
- **`calculation`**: Performs bounded arithmetic (`+`, `-`, `*`, `/`, `//`, and `**` with exponent limits) between large integers safely without `eval()`.
- **`sleep`**: Simulates non-blocking wait times (bounded between 0 and 300 seconds).

---

## Key Features

- **Decoupled Architecture**: Producers and worker consumers run in separate OS processes.
- **Atomic Job Claiming**: Uses conditional SQL updates (`WHERE id = :id AND status = 'pending'`) to eliminate race conditions across multiple workers.
- **Multi-Worker Scaling**: Simple bash script (`scripts/start-workers.sh`) to launch and supervise $N$ concurrent workers with automatic signal trapping (`SIGINT`/`SIGTERM`) to prevent orphaned processes.
- **Built-in Web Dashboard**: A responsive single-page dashboard (`frontend/index.html`) with real-time polling to enqueue jobs and inspect results visually.
- **Fault Recovery**: Automatically resets stale/abandoned jobs back to `pending` after a configurable timeout (default: 60 seconds).
- **Multipart File Upload**: Dedicated endpoint (`/api/jobs/upload`) to upload images directly into the queue.

---

## Project Structure

```text
message_queue/
├── backend/
│   ├── api/             # FastAPI routers and route handlers
│   ├── database/        # Database engine, session, and connection setup
│   ├── models/          # SQLAlchemy ORM models (Job)
│   ├── schemas/         # Pydantic validation schemas & discriminators
│   ├── services/        # Business logic for job creation & querying
│   ├── workers/         # Worker process, task handlers, & recovery loop
│   └── main.py          # FastAPI application entry point
├── frontend/
│   └── index.html       # Web dashboard for enqueuing and monitoring jobs
├── scripts/
│   ├── start-api.sh     # Starts the FastAPI server with reload
│   ├── start-worker.sh  # Starts a single worker process
│   └── start-workers.sh # Starts multiple concurrent workers with argument
├── assets/
│   ├── image/          # Uploaded source images
│   └── output_images/  # Compressed output images
├── pyproject.toml       # Project metadata and dependencies
└── jobs.db              # SQLite database (auto-created on first run)
```

---

## Environment Configuration

Configure environment variables in a `.env` file at the project root or inside `backend/.env`:

```bash
# Database connection string
DATABASE_URL=sqlite:///./jobs.db

# Recovery & directory paths (optional)
DEAD_JOB_RETRY_INTERVAL=60
ROOT_DIR=.
ASSETS_DIR=./assets
IMG_DIR=./assets/image
IMG_OUTPUT_DIR=./assets/output_images
```

---

## Getting Started

### Prerequisites

- **Python 3.12+**
- [**uv**](https://github.com/astral-sh/uv) (fast Python package manager)

### Installation

Clone the repository and install all dependencies:

```bash
uv sync
```

---

## Running the Application

### 1. Start the API Server

Using the helper script:
```bash
./scripts/start-api.sh
```

Or using `uv` directly:
```bash
uv run uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

- API Base URL: `http://localhost:8000`
- Interactive OpenAPI Docs (Swagger): `http://localhost:8000/docs`

---

### 2. Start Worker Processes

#### Single Worker:
```bash
./scripts/start-worker.sh
```
*(Or directly: `uv run python -m backend.workers.worker`)*

#### Multiple Workers (Concurrently):
Pass the number of workers as an argument (defaults to 4 if omitted):

```bash
# Start 4 workers (default)
./scripts/start-workers.sh

# Start 8 workers
./scripts/start-workers.sh 8
```

> **Note**: Press `Ctrl+C` to terminate the worker pool. The script cleanly intercepts `SIGINT`/`SIGTERM` and shuts down all spawned background worker processes.

---

### 3. Open the Web Dashboard

Open `frontend/index.html` directly in any web browser, or serve it locally:

```bash
# Serve frontend on port 3000
python3 -m http.server 3000 --directory frontend
```

Navigate to `http://localhost:3000` to interactively dispatch sleep, calculation, or image compression jobs and monitor their live progress.

---

## Using the API (cURL Examples)

### 1. Enqueue a Sleep Job

```bash
curl -X POST http://localhost:8000/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "type": "sleep",
    "payload": {
      "seconds": 5
    }
  }'
```

### 2. Enqueue a Calculation Job

Supported operators: `+`, `-`, `*`, `/`, `//`, `**`

```bash
curl -X POST http://localhost:8000/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "type": "calculation",
    "payload": {
      "first": 12,
      "second": 4,
      "operator": "*"
    }
  }'
```

### 3. Enqueue an Image Compression Job

#### Via Direct Multipart Upload:
```bash
curl -X POST http://localhost:8000/api/jobs/upload \
  -F "file=@/path/to/sample.jpg"
```

#### Via JSON Payload (Referencing Existing File):
```bash
curl -X POST http://localhost:8000/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "type": "image",
    "payload": {
      "image_path": "assets/image/sample.jpg",
      "operation": "compress"
    }
  }'
```

### 4. Query Jobs and Inspect Status

List all jobs:
```bash
curl http://localhost:8000/api/jobs
```

Inspect a specific job by ID:
```bash
curl http://localhost:8000/api/jobs/<job-id>
```

API health check:
```bash
curl http://localhost:8000/
```

---

## Delivery Semantics & Failure Recovery

- **At-Least-Once Processing**: PyQueue operates on at-least-once delivery guarantees. If a worker process is killed abruptly while executing a task, the recovery loop detects that the job has remained in `running` status past the timeout (60 seconds) and automatically resets it to `pending`.
- **Idempotency**: Because abandoned jobs may be retried, handlers should be designed to be idempotent.
- **Throttling**: Workers use a 1-second polling interval to balance responsiveness with minimal CPU and database contention.

---

## Known Limitations & Future Roadmap

PyQueue is intentionally built as a lightweight queue for learning and local tooling. It is not intended as a drop-in replacement for enterprise-scale distributed message brokers.

- **Concurrency & Storage**: SQLite is single-file based; high concurrency across dozens of workers can hit database write locks. Moving to PostgreSQL with `FOR UPDATE SKIP LOCKED` is planned for higher concurrency.
- **Heartbeats & Leases**: Currently uses a fixed 60-second recovery window. Dynamic worker heartbeats will be introduced so very long tasks are not prematurely requeued.
- **Exponential Backoff & Dead-Letter Queue (DLQ)**: Retries currently reset immediately to pending; exponential backoff with jitter and max attempt limits will be added.
