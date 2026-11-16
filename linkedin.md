Message queues are an essential component of modern infrastructure.
They decouple fast HTTP request-response cycles from slow and heavy compute tasks by persisting task metadata in a queue and they are executed by independent worker processes.

They avoid freezing the server for long-running tasks, absorb traffic spikes and guarantee that requests are not lost in case of server failure.

To understand this component, I implemented a simple message queue system using Python, FastAPI, SQLite and SQLAlchemy.

What I've implemented:

- Producer API: Accepts jobs, validates requests using Pydantic, and persists them to SQLite.
- Atomic Job Claiming: Prevents multiple workers from picking up the same job by using atomic database updates, avoiding duplicate execution and wasted compute resources.
- Independent Workers: Independent processes that poll the queue and execute tasks concurrently.
- Crash Recovery: Detects abandoned/failed jobs and requeues them using at-least-once delivery semantics.
- Job Tracking: Clients can track execution states, outputs, and error tracebacks through short polling.

I have programmed the queue to accept several tasks like image resizing, arithmetic calculations and sleep tasks.

Producer and multiple instances of Consumer can be started with shell scripts.

Building this gave me a much better appreciation of the engineering behind tools like Celery, RabbitMQ, and Amazon SQS.

GitHub Repo: https://github.com/sankalp6115/message_queue_advanced

#Python #FastAPI #BackendDevelopment #SystemDesign