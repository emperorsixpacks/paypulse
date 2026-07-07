from arq import cron
from arq.connections import RedisSettings

from src.paypulse.core.settings import settings
from src.paypulse.workers.billing_worker import run_billing_cycle
from src.paypulse.workers.dunning_worker import run_dunning_cycle
from src.paypulse.workers.webhook_worker import deliver_webhook


class WorkerSettings:
    functions = [deliver_webhook]
    cron_jobs = [
        cron(run_billing_cycle, hour=set(range(24)), minute=0),
        cron(run_dunning_cycle, hour=set(range(24)), minute=30),
    ]
    redis_settings = RedisSettings.from_dsn(settings.get_redis_url())
    max_jobs = settings.ARQ_MAX_JOBS
    job_timeout = settings.ARQ_JOB_TIMEOUT
    keep_result = settings.ARQ_KEEP_RESULT
    max_tries = settings.ARQ_MAX_TRIES
    queue_read_delay = 100
    redis_queue_name = settings.ARQ_QUEUE_NAME
    redis_stream_name = settings.ARQ_STREAM_NAME
    max_enqueue_interval = 1
