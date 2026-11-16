# PyQueue: Next Gameplan & Roadmap

A structured, phased roadmap to evolve PyQueue into an advanced, production-grade distributed task queue. Each phase builds upon the previous one to reinforce key distributed systems and backend engineering principles.

---

## Active & Upcoming Fixes

- [x] Standardize worker launch scripts in `scripts/start-workers.sh` with argument-based concurrency.
- [ ] Implement exponential backoff and jitter for worker polling and retry scheduling.
- [ ] Transition from static recovery timeout to worker heartbeats and leases.

---

## Phase 0: Clean Project Foundation

**Goal**: Make the project frictionless to run, test, and extend.

1. Structure into modular layers:
   - `app/api/`: Request validation, routing, HTTP controllers.
   - `app/services/`: Core business logic and database interactions.
   - `app/workers/`: Worker process, dispatchers, handlers, and recovery.
   - `app/models/`: SQLAlchemy ORM definitions.
   - `app/schemas/`: Pydantic input/output schemas.
   - `tests/`: Automated unit and integration tests.
2. Standardize CLI execution scripts (`scripts/start-api.sh`, `scripts/start-worker.sh`, `scripts/start-workers.sh`).
3. Add environment configuration (`.env`) for DB URL, polling interval, and recovery timeouts.
4. Containerize with `Dockerfile` and `docker-compose.yml` for unified execution.
5. Add code quality tooling (Ruff / Black / Pytest).

> **Done When**: A new developer can clone the repo, run a single startup command, and run passing tests out of the box.

---

## Phase 1: Strong Job Model and API Validation

**Goal**: Make invalid jobs impossible to enqueue.

1. Implement strongly typed Pydantic models with discriminator tags (`type`).
2. Supported task types:
   - `sleep`: Pause execution.
   - `calculation`: Arithmetic expressions.
   - `image`: Image resizing and compression.
3. Validate payload boundaries:
   - Constrain sleep durations (`0 <= seconds <= 300`).
   - Allowlist math operators (`+`, `-`, `*`, `/`, `//`, `**`).
   - Bound numeric magnitudes and exponent values to prevent Denial of Service (DoS).
4. Separate internal ORM entities from client-facing `JobResponse` schemas.
5. Provide query filtering on `GET /api/jobs?status=...&limit=...`.

> **Done When**: Unsupported job types or invalid payloads return informative `422 Unprocessable Entity` responses prior to database insertion.

---

## Phase 2: State Machine and Atomic Claiming

**Goal**: Make state transitions explicit, predictable, and concurrency-safe.

1. Formally define lifecycle state transitions:
   ```text
   pending  ───> running ───> completed
      │            │
      │            └───> failed
      │            │
      │            └───> pending (lease expired / retry)
      └───> cancelled
   ```
2. Extend database schema:
   - `attempts` / `max_attempts`
   - `available_at` (for delayed jobs and retry backoff)
   - `started_at`, `completed_at`, `failed_at`
   - `worker_id`
   - `lease_expires_at`
3. Add composite indexes for efficient querying:
   - `(status, available_at, created_at)`
   - `(lease_expires_at)`
4. Claim jobs atomically using conditional `UPDATE ... WHERE status = 'pending'` transactions to eliminate race conditions.

> **Done When**: Multiple concurrent workers process a high volume of queued jobs without duplicate claims or double execution.

---

## Phase 3: Leases, Heartbeats, and Crash Recovery

**Goal**: Safely recover from worker crashes without terminating or re-running healthy long-running jobs.

1. Generate a unique `worker_id` (e.g., UUID or hostname + PID) when each worker boots.
2. On claiming a job:
   - Transition status to `running`.
   - Assign `worker_id`.
   - Set initial `lease_expires_at` (e.g., 30 seconds ahead).
3. Background heartbeat thread in worker periodically renews `lease_expires_at` while the job is active.
4. Recovery process reclaims only jobs where `status = 'running'` AND `lease_expires_at < CURRENT_TIMESTAMP`.
5. Require matching `worker_id` when marking a job `completed` or `failed`.
6. Graceful shutdown handler: intercepts `SIGINT`/`SIGTERM` to safely finish active work or release leases before termination.

> **Done When**: Forcefully killing a worker mid-execution safely returns its job to `pending`, while legitimate long-running jobs continue uninterrupted.

---

## Phase 4: Retries and Dead-Letter Queue (DLQ)

**Goal**: Robustly handle transient failures without infinite failure loops.

1. Categorize errors into transient (retryable) vs permanent (non-retryable):
   - **Transient**: Network glitch, file system lock contention.
   - **Permanent**: Validation failure, unsupported parameters, division by zero.
2. Implement exponential backoff with jitter:
   $$\text{backoff} = \min(\text{max\_backoff}, \text{base} \times 2^{\text{attempts}}) \pm \text{jitter}$$
3. Return failed retryable jobs to `pending` with `available_at` set into the future.
4. When `attempts >= max_attempts`, mark status as `dead_letter` (DLQ).
5. Endpoints:
   - `GET /api/jobs?status=dead_letter`
   - `POST /api/jobs/{id}/retry` (manual retry trigger from DLQ)

> **Done When**: Transient errors automatically retry with backoff and permanently failing jobs cleanly land in DLQ.

---

## Phase 5: Idempotency and Delivery Guarantees

**Goal**: Guarantee at-least-once delivery while protecting against duplicate processing side effects.

1. Accept an optional `idempotency_key` on `POST /api/jobs`.
2. Enforce uniqueness per idempotency key to prevent duplicate job creation upon client retries.
3. Return the original existing job if duplicate requests are received.
4. Ensure task handlers are idempotent (e.g., deterministic file output names, checking prior state before mutations).

> **Done When**: Client network retries cannot cause redundant job execution.

---

## Phase 6: Named Queues, Priority, and Scheduling

**Goal**: Evolve from a single FIFO queue into a prioritized multi-queue system.

1. Add `queue_name` column (default: `"default"`).
2. Allow workers to subscribe to specific named queues (e.g., `uv run python -m backend.workers.worker --queue images`).
3. Add integer `priority` levels (e.g., 1 to 10).
4. Order job claiming by:
   - `priority DESC`
   - `created_at ASC`
5. Support scheduled delayed execution (`POST /api/jobs` with `run_at` timestamp).

> **Done When**: Heavy image processing tasks do not block critical fast-path calculation or notification jobs.

---

## Phase 7: PostgreSQL Migration & High Concurrency

**Goal**: Scale horizontally across multiple nodes with row-level locking.

1. Integrate Alembic for database migrations.
2. Support PostgreSQL connection pool.
3. Replace SQLite table locking with `SELECT ... FOR UPDATE SKIP LOCKED` for lock-free parallel job claiming across dozens of worker nodes.
4. Keep SQLite as an optional local development driver.

> **Done When**: Multiple distributed API replicas and worker nodes operate concurrently against PostgreSQL without lock contention.

---

## Phase 8: Observability and Operations

**Goal**: Gain full operational visibility into queue health and throughput.

1. Implement structured JSON logging:
   - `trace_id`, `job_id`, `worker_id`, `queue_name`, `attempt`, `duration_ms`.
2. Health and readiness endpoints:
   - `GET /health` (liveness probe)
   - `GET /ready` (database connectivity probe)
3. Prometheus metrics:
   - `jobs_enqueued_total`
   - `jobs_completed_total`
   - `jobs_failed_total`
   - `job_execution_duration_seconds` (histogram)
   - `queue_depth` (gauge)
4. Expose operational dashboard summarizing current queue velocity.

---

## Recommended Next Step

Begin with **Phase 3 (Leases & Heartbeats)**. It eliminates the limitation where tasks longer than the recovery window risk duplicate execution by another worker. Follow with **Phase 4 (Retries & Dead-Letter Queue)** for production-level resilience.
