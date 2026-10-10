# PyQueue

PyQueue is a small, persistent background-job queue built with FastAPI,
SQLite, and SQLAlchemy. It is designed for local projects and for learning the
core ideas behind a worker queue.

## What it does

```text
Client -> FastAPI producer -> SQLite jobs table -> worker process
```

1. The API validates and stores a job, then immediately returns its ID.
2. A separate worker polls for pending jobs, claims one safely, and runs it.
3. The worker stores the result or error so the API can report job status.

Supported jobs:

- `sleep`: pauses for 0-300 seconds.
- `calculation`: performs a bounded integer calculation.

## Features

- Persistent jobs and results in SQLite.
- Separate producer (FastAPI) and consumer (worker) processes.
- Input validation with Pydantic.
- Atomic conditional job claiming for simple multi-worker use.
- Job states: `pending`, `running`, `completed`, and `failed`.
- Error storage and basic recovery of abandoned jobs.

## Run locally

Install dependencies:

```bash
uv sync
```

Start the API in one terminal:

```bash
uv run uvicorn app.main:app --reload
```

Start one worker in another terminal:

```bash
uv run python -m app.workers.worker
```

Optionally start four workers from the project root:

```bash
./app/workers/multiprocessing.sh
```

## Use the API

Enqueue a sleep job:

```bash
curl -X POST http://localhost:8000/api/jobs \
  -H "Content-Type: application/json" \
  -d '{"type":"sleep","payload":{"seconds":5}}'
```

Enqueue a calculation job:

```bash
curl -X POST http://localhost:8000/api/jobs \
  -H "Content-Type: application/json" \
  -d '{"type":"calculation","payload":{"first":10,"second":20,"operator":"+"}}'
```

Inspect jobs:

```bash
curl http://localhost:8000/api/jobs
curl http://localhost:8000/api/jobs/<job-id>
```

## Important limitations

This is intentionally a small local queue, not a replacement for Celery, RabbitMQ, Redis, or Kafka.

- SQLite is best for a single machine and modest traffic.
- The worker polls once per second instead of receiving pushed messages.
- Jobs have no retry policy, priority, scheduling, or cancellation yet.
- Processing is at-least-once in failure situations: an abandoned job may be
  re-run after the ten-minute recovery timeout.
- Keep custom handlers shorter than the recovery timeout unless you extend the
  implementation.

Those limitations are useful learning points, not hidden behavior.


## Future Increments
- Implementing automated testing of APIs
