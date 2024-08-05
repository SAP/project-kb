# Evaluate Prospector

This folder contains the scripts used for evaluating Prospector's reports (created and used in Summer 2024). The folder is structured as follows:

1. **Data** folder: contains input data, Prospector reports and results of the analysis of the Prospector reports.
2. **Scripts**: The scripts used for running Prospector on a batch of CVEs, and for analysing the created reports.

Prospector is run in the following way in this evaluation:

First, the five docker containers must be started with `make docker-setup` or manually with `docker` commands. Once they are running, `docker ps` should show the following:

```bash
CONTAINER ID   IMAGE                COMMAND                  CREATED          STATUS          PORTS                                       NAMES
c73aed108475   prospector_backend   "python ./service/ma…"   47 minutes ago   Up 47 minutes   0.0.0.0:8000->8000/tcp, :::8000->8000/tcp   prospector_backend_1
2e9da86b09a8   prospector_worker    "/usr/local/bin/star…"   47 minutes ago   Up 47 minutes                                               prospector_worker_1
b219fd6219ed   adminer              "entrypoint.sh php -…"   47 minutes ago   Up 47 minutes   0.0.0.0:8080->8080/tcp, :::8080->8080/tcp   prospector_adminer_1
9aacdc04f7c5   postgres             "docker-entrypoint.s…"   47 minutes ago   Up 47 minutes   0.0.0.0:5432->5432/tcp, :::5432->5432/tcp   db
7c540450ab76   redis:alpine         "docker-entrypoint.s…"   47 minutes ago   Up 47 minutes   0.0.0.0:6379->6379/tcp, :::6379->6379/tcp   prospector_redis_1
```

[`dispatch_jobs.py`](#running-prospector-on-multiple-cves-dispatch_jobspy) creates jobs with the `prospector()` function in them and enqueues
them in a Redis Queue, from which the `prospector_worker` container fetches jobs and executes them. To visualise what is going on, run
`docker attach prospector_worker_1` to see the usual console output. In order to change something inside the container, run `docker exec -it prospector_worker_1 bash` to open an interactive bash shell.

## Command Line Options

All scripts are called from `main.py`, depending on the CL flags that are set. The following flags can be set:

1. `-i`: Sets the filename of the file in the input data path.
2. `-c`: Allows you to select a subset of CVEs, instead of all CVEs from the input data (eg. `-c CVE-2020-1925, CVE-2018-1234`)
3. `-e`: For *execute*, dispatched jobs for all CVEs from the input data (or the subset if `-c` is set) to the Redis Queue (`dispatch_jobs.py`).
4. `-a`: Analyses the reports created by Propsector (`analysis.py`)
5. `-s`: Analyses the statistics part of the Prospector reports (eg. to analyse execution times, `analyse_statistics.py`)
6. `-eq`: For *empty queue*, to empty the jobs left on the queue.
7. `-co`: For *count*, to count how many of the CVEs in the input data have a corresponding report.

## Configuration File

The configuration file has two parts to it: a main part and a Prospector settings part, which is a copy of a part of the original Prospector `config.yaml` file.

The main part at the top allows you to set the path to where the input data can be found, where Prospector reports should be saved to and where analysis results should be saved to.

The Prospector part allows you to set the settings for Prospector (independent from the Prospector settings used when running Prospector with `./run_prospector`). **Watch out**: Since the `prospector_worker` container is created in the beginning with the current state of the `config.yaml`, simply saving any changes in `config.yaml` and dispatching new jobs will still run them with the old configuration. For new configuration parameters to take effect, either destroy the containers with `make docker-clean` and rebuild them with `make docker-setup` or open an interactive shell to the container and make your changes to `config.yaml` in there.

## Script Files explained

### Running Prospector on multiple CVEs (`dispatch_jobs.py`)

The code for running Prospector is in `dispatch_jobs.py`. It exctracts CVE IDs from the data given in the path constructed as: `input_data_path` + the `-i` CL parameter. It then dispatches a job for each CVE ID to the queue, from where these jobs get executed.