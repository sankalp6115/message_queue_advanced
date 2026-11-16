# PyQueue

PyQueue is a lightweight, persistent background-job queue built with FastAPI, SQLite, and SQLAlchemy. It is designed for local projects, experimentation, and learning the fundamental architecture behind distributed worker queues without external dependencies like Redis or RabbitMQ.

## Architecture

```text
┌──────────┐        HTTP Request        ┌───────────────────────┐
│  Client  │ ─────────────────────────> │   FastAPI Producer    │
└──────────┘                            └───────────────────────┘
     ▲                                              │
     │ GET /api/jobs/{id}                           │ Store Job
     │                                              ▼
┌──────────┐      Poll & Atomic Claim   ┌───────────────────────┐
│  Worker  │ <───────────────────────── │   SQLite jobs Table   │
└──────────┘                            └───────────────────────┘
     │                                              ▲
     └───────────── Save Result / Error ────────────┘
```

1. **Producer (FastAPI)**: Validates incoming payloads and persists a new job record with `pending` status, returning a job ID immediately.
2. **Database (SQLite)**: Acts as the persistent queue, tracking job states, timestamps, payloads, results, and errors.
3. **Consumer (Worker)**: A decoupled background process that polls for `pending` jobs, atomically claims them by transitioning them to `running`, executes the task, and commits `completed` or `failed` status with the output.

### Supported Job Types

- **`sleep`**: Pauses for a bounded duration (0–300 seconds).
- **`calculation`**: Performs safe arithmetic (`+`, `-`, `*`, `/`, `//`, `**` with power bounds) between bounded integers.
- **`image`**: Compresses images across multiple quality levels (`25`, `50`, `75`, `90`) and saves the outputs to `assets/output_images/`.

## Features

- **Persistent storage**: Jobs and execution results survive application restarts.
- **Process isolation**: Producers and consumers run in separate OS processes.
- **Input validation**: Strongly typed payloads validated using Pydantic discriminators.
- **Atomic job claiming**: Conditional SQL update prevents race conditions across multiple workers.
- **State tracking**: Full lifecycle states (`pending`, `running`, `completed`, `failed`).
- **Failure handling & recovery**: Captures execution errors; automatically recovers stale/abandoned `running` jobs after a recovery timeout.
- **Multi-worker scaling**: Simple script to launch multiple concurrent worker processes with argument-based scaling.

## Getting Started

### Prerequisites

- Python 3.12+
- [`uv`](https://github.com/astral-sh/uv) (recommended package and project manager)

### Installation

Clone the repository and install dependencies:

```bash
uv sync
```

### Running Locally

You can use the helper bash scripts in `scripts/` or invoke `uv` directly.

#### 1. Start the API Server

Using the script:
```bash
./scripts/start-api.sh
```

Or using `uv` directly:
```bash
uv run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. Interactive OpenAPI documentation is accessible at `http://localhost:8000/docs`.

#### 2. Start a Worker

In a separate terminal, launch a single worker:

Using the script:
```bash
./scripts/start-worker.sh
```

Or using `uv` directly:
```bash
uv run python -m app.workers.worker
```

#### 3. Start Multiple Workers

To start multiple concurrent workers, run `start-workers.sh` with the number of workers as an argument (defaults to 4 if omitted):

```bash
# Start 4 workers (default)
./scripts/start-workers.sh

# Start a custom number of workers (e.g., 6)
./scripts/start-workers.sh 6
```

Press `Ctrl+C` at any time to gracefully terminate all running worker processes.

## Using the API

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

```bash
curl -X POST http://localhost:8000/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "type": "calculation",
    "payload": {
      "first": 15,
      "second": 3,
      "operator": "*"
    }
  }'
```

### 3. Enqueue an Image Compression Job

#### Via direct file upload:
```bash
curl -X POST http://localhost:8000/api/jobs/upload \
  -F "file=@/path/to/image.jpg"
```

#### Via JSON payload:
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

### 4. Query Jobs and Status

List all jobs:
```bash
curl http://localhost:8000/api/jobs
```

Inspect a specific job by ID:
```bash
curl http://localhost:8000/api/jobs/<job-id>
```

Health check:
```bash
curl http://localhost:8000/
```

## Important Limitations

PyQueue is intentionally built as a lightweight local queue for educational and personal utility purposes. It is not an out-of-the-box replacement for enterprise solutions such as Celery, Temporal, Redis Streams, or RabbitMQ.

- **Storage backend**: SQLite is optimized for single-node deployments and moderate concurrency. High write concurrency across dozens of workers may encounter SQLite lock contention.
- **Polling mechanism**: Workers poll every second rather than using push notifications or event-driven sockets.
- **Delivery semantics**: At-least-once processing in failure scenarios. If a worker process abruptly dies mid-task, the job will be reclaimed after the recovery timeout. Tasks should be written to be idempotent.
- **Task timeouts**: Custom tasks should be designed to complete well within the recovery window unless an explicit heartbeat mechanism is added.
