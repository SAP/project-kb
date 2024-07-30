# Evaluate Prospector

This folder contains code to run the evaluation of Prospector using Redis Queue. This means that the `prospector()` function will be packaged as a job and executed by the `prospector_worker` container.

To see what's going on, visualise the output of the worker container with:

```bash
docker attach prospector_worker_1
```

To interact with the worker container (or any other container), run:
```bash
docker exec -it prospector_worker_1 bash
```


## Settings

Just like when running Prospector, there is also a configuration file for the evaluation code in this folder: `evaluation/config.yaml`. It contains the same fields as `config.yaml`, bundled in the `prospector_settings` field, so you can set everything as usual in one central place.
All other settings (outside of the `prospector_settings`) are for setting up evaluation specific parameters.

## Enqueuing Jobs



### Which CVEs should Prospector be run on?

The evaluation code expects data input in the form of CSV files with the following columns: `(CSV: ID;URL;VERSIONS;FLAG;COMMITS;COMMENTS)`.

First, if you have your input data saved somewhere else than `/evaluation/data/input/`, please change the `input_data_path` accordingly.
Give your dataset a descriptive name, such as `steady-dataset.csv`. You can specify
which dataset you would want to use when running the CL command for evaluation [(List of Command Line Options)](#command-line-options).


## Run Evaluation

### Dispatch Prospector Jobs
To dispatch several Prospector jobs to the queue, use:

```bash
python3 evaluation/run_multiple -i <name_of_dataset> -e
```

### List of Command Line Options

* `-i` or `--input`: Specify the input file (likely a CSV with vulnerability data)
* `-e` or `--execute`: Run Prospector on the input data
* `-a` or `--analyze`: Analyze the results of previous Prospector runs
* `-o` or `--output`: Specify an output file (for certain operations)
* `-r` or `--rules`: Perform rules analysis
* `-f` or `--folder`: Specify a folder to analyze
* `-c` or `--cve`: Specify a particular CVE to analyze
* `-p` or `--parallel`: Run in parallel on multiple CVEs


## Exisiting Datasets

1. `d63`: Dataset of CVEs and their fixing commits used in D6.3 of AssureMOSS. Formerly called `tracer_dataset_correct_full_unsupervised.csv`.