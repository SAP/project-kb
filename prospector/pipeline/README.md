# Pipeline Usage of Prospector


The pipeline works in the following way:

1. `get_cve_data()` of `filter_entries.py` first fetches the most recent CVEs' raw data.
2. This raw data get saved to the `vulnerability` table of the database.
3. Then this raw vulnerability data gets fetched from the database and filtered (`process_cve_data()` of `filter_entries.py`)
4. For each filtered CVE, a job (essentially the Prospector function and the report generation function) is created and enqueued in the Redis Queue using `enqueue_jobs()` from `job_creation.py`.

## Use the Pipeline

For the pipeline to work, first run

```bash
make docker-setup
```

to create the following five containers:

```bash
CONTAINER ID   IMAGE                COMMAND                  CREATED          STATUS          PORTS                                       NAMES
77e4b01ada4d   prospector_backend   "python ./service/ma…"   58 minutes ago   Up 58 minutes   0.0.0.0:8000->8000/tcp, :::8000->8000/tcp   prospector_backend_1
57a30c903a9a   prospector_worker    "/usr/local/bin/star…"   58 minutes ago   Up 58 minutes                                               prospector_worker_1
2ea00e47ac71   redis:alpine         "docker-entrypoint.s…"   58 minutes ago   Up 58 minutes   0.0.0.0:6379->6379/tcp, :::6379->6379/tcp   prospector_redis_1
120d3502ee51   postgres             "docker-entrypoint.s…"   58 minutes ago   Up 58 minutes   0.0.0.0:5432->5432/tcp, :::5432->5432/tcp   db
1d9acef24637   adminer              "entrypoint.sh php -…"   58 minutes ago   Up 58 minutes   0.0.0.0:8080->8080/tcp, :::8080->8080/tcp   prospector_adminer_1
```

Then enqueue the latest CVEs as jobs by running `python3 pipeline/main.py`.

### Increase the number of workers

Adjust the number of workers in `etc_supervisor_confd_rqworker.conf.j2`:

```bash
...
numprocs=2
...
```

## Observe Pipeline

View the database on `localhost:8080`.

View the fetched vulnerabilities and generated reports on `localhost:8000`.

View worker output in the terminal by running `docker attach prospector_worker_1` or the output in `prospector.log` (even though this can be difficult to read with more than 1 worker, because the logging gets all mixed up between workers).

