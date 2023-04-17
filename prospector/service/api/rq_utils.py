import redis
from rq import Queue
from util.config_parser import parse_config_file

config = parse_config_file()
redis_url = config.redis_url


redis_connection = redis.from_url(redis_url)

queue = Queue(connection=redis_connection)


# get job ids
def get_job_ids(job_registry):
    return job_registry.get_job_ids()


def get_all_job_ids():
    all_job_ids = []
    all_job_ids.extend(get_job_ids(queue.started_job_registry))
    all_job_ids.extend(queue.job_ids)
    all_job_ids.extend(get_job_ids(queue.failed_job_registry))
    all_job_ids.extend(get_job_ids(queue.deferred_job_registry))
    all_job_ids.extend(get_job_ids(queue.finished_job_registry))
    all_job_ids.extend(get_job_ids(queue.scheduled_job_registry))
    return all_job_ids


# get job given its id
def get_job_from_id(job_id):
    job = queue.fetch_job(job_id)
    return job


# get all jobs
def get_all_jobs():
    # init all_jobs list
    all_jobs = []
    # get all job ids
    all_job_ids = get_all_job_ids()
    # iterate over job ids list and fetch jobs
    for job_id in all_job_ids:
        all_jobs.append(get_job_from_id(job_id))
    return all_jobs
