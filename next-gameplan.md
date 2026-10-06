## fixes + extensions
worker launch path in multiprocessing.sh
backoff

Here’s a strong, portfolio-ready roadmap. Build it in this order—each phase leaves you with a working system and teaches one real backend concept.

## Phase 0 — Clean project foundation

Goal: make the project easy to run, test, and extend.

1. Restructure into clear modules:
   - `app/api/`
   - `app/services/`
   - `app/workers/`
   - `app/models/`
   - `tests/`
2. Run the worker as a module: `python -m app.worker.worker`.
3. Add environment-based configuration for database URL, polling interval, lease duration, and retry limits.
4. Add Dockerfile and Docker Compose with separate `api` and `worker` services.
5. Add Ruff/Black and Pytest.

Done when: a new developer can run the API and worker with one documented command, and tests run in CI.

## Phase 1 — Strong job model and API

Goal: make invalid jobs impossible to enqueue.

1. Replace generic `type: str` and `payload: dict` with validated Pydantic job schemas.
2. Support explicit task types:
   - `sleep`
   - `calculation`
3. Validate payload constraints:
   - sleep duration range;
   - allowed arithmetic operators;
   - safe number/exponent bounds.
4. Add response models so you never return raw ORM objects directly.
5. Add API endpoints:
   - `POST /jobs`
   - `GET /jobs/{job_id}`
   - `GET /jobs?status=&limit=&cursor=`
   - `POST /jobs/{job_id}/cancel`

Done when: unsupported job types or malformed payloads return a useful `422` error before entering the queue.

## Phase 2 — Correct state machine and atomic claiming

Goal: make job transitions explicit and safe.

1. Define allowed transitions:

```text
pending → running → completed
pending → running → failed
pending → cancelled
running → pending     (lease expired / retry)
running → failed
```

2. Add database fields:
   - `attempts`
   - `max_attempts`
   - `available_at`
   - `started_at`
   - `completed_at`
   - `failed_at`
   - `worker_id`
   - `lease_expires_at`
3. Add indexes for job fetching:
   - `(status, available_at, created_at)`
   - `(lease_expires_at)`
4. Claim jobs with an atomic database update, not a read-then-unprotected-write pattern.

Done when: four workers can process many jobs without one job being claimed twice.

## Phase 3 — Leases, heartbeats, and crash recovery

Goal: safely recover from worker crashes without duplicating healthy long jobs.

1. Generate a unique `worker_id` at worker startup.
2. When claiming a job:
   - set `status=running`;
   - record `worker_id`;
   - set `lease_expires_at`.
3. During execution, heartbeat periodically to extend the lease.
4. Requeue only jobs with expired leases.
5. Require the same `worker_id` when completing/failing a job.
6. Add a graceful shutdown handler:
   - stop claiming new jobs;
   - finish or safely release the current lease.

Done when: killing a worker mid-task causes the job to be retried, while a long healthy task is never mistakenly requeued.

## Phase 4 — Retries and dead-letter jobs

Goal: handle real-world transient failures.

1. Classify errors:
   - retryable: timeout, temporary external service failure;
   - permanent: invalid input, unsupported operation.
2. On retryable failure:
   - increment `attempts`;
   - calculate exponential backoff;
   - add random jitter;
   - set `available_at` in the future;
   - return job to `pending`.
3. When `attempts >= max_attempts`, mark the job `dead_letter`.
4. Add endpoints:
   - `GET /jobs?status=dead_letter`
   - `POST /jobs/{job_id}/retry`
5. Store error type, message, and traceback safely.

Done when: a failing task retries predictably and ends in a visible dead-letter state instead of endlessly cycling.

## Phase 5 — Idempotency and delivery guarantees

Goal: make duplicate delivery safe.

1. Add an optional `idempotency_key` to `POST /jobs`.
2. Enforce a unique constraint for the key per queue/task type.
3. Return the original job if the client repeats a submission.
4. Document the guarantee correctly: **at-least-once delivery**.
5. Design handlers to be idempotent—for example, “send an email for order X” should record that order X was already processed.

Done when: network retries from producers do not enqueue duplicate work, and a retried worker task cannot cause harmful duplicate side effects.

## Phase 6 — Queues, routing, priority, and scheduling

Goal: evolve from one task table into a flexible queue platform.

1. Add `queue_name` to jobs.
2. Let workers subscribe to one or more queues.
3. Add priority (`0–10`, for example).
4. Fetch jobs by:
   - available time;
   - priority;
   - creation time.
5. Support delayed jobs using `available_at`.
6. Add queue-level concurrency/rate limits.

Done when: email, image-processing, and payment queues can be consumed independently without starving each other.

## Phase 7 — PostgreSQL migration

Goal: support actual multi-worker workload safely.

1. Add Alembic migrations.
2. Move from SQLite to PostgreSQL.
3. Use row locking such as `FOR UPDATE SKIP LOCKED` for high-concurrency job claiming.
4. Keep SQLite as a local development option if desired.
5. Test with multiple API instances and multiple workers.

Done when: multiple workers and API replicas can run safely against one shared database.

## Phase 8 — Observability and operations

Goal: make it operable like a real backend service.

1. Add structured JSON logs with:
   - `job_id`
   - `worker_id`
   - queue name
   - attempt number
   - duration
2. Add health endpoints:
   - `/health`
   - `/ready`
3. Add Prometheus-style metrics:
   - pending jobs;
   - jobs processed;
   - failures;
   - retries;
   - queue latency;
   - execution duration.
4. Add request/job correlation IDs.
5. Create a simple dashboard endpoint for queue stats.

Done when: you can quickly answer “is the queue stuck, slow, or failing?”

## Phase 9 — Security and production polish

Goal: make the project deployment-ready.

1. Add API-key or JWT authentication for job submission and inspection.
2. Add per-client rate limits and payload size limits.
3. Sanitize errors returned through the API.
4. Add retention and cleanup policies for completed jobs.
5. Add CI:
   - formatting;
   - unit tests;
   - integration tests;
   - Docker build.

Done when: the project has a clean README, architecture diagram, test suite, CI, deployment instructions, and documented limits.

## Best “next implementation” choice

Start with **Phase 3: leases and heartbeats**. It fixes the most important reliability flaw in the current project: a long-running task can currently be considered stale and executed again by another worker.

After that, implement Phase 4 retries/dead-letter jobs. Together, those two features make this feel like a genuine backend queue rather than a basic background-task demo.