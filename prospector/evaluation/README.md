# Evaluate Prospector

This folder contains code to run the evaluation of Prospector.

## Settings

Just like when running Prospector, there is also a configuration file for the evaluation code in this folder: `evaluation/config.yaml`.
This allows you to select data and set Prospector up in a certain way in one central place.

### How should Prospector be run?

Prospector can either be run containerised or not, set this with the `run_containerised` variable in `config.yaml`.

### Which CVEs should Prospector be run on?

The evaluation code expects data input in the form of CSV files with the following columns: `(CSV: ID;URL;VERSIONS;FLAG;COMMITS;COMMENTS)`.

First, if you have your input data saved somewhere else than `/evaluation/data/input/`, please change the `input_data_path` accordingly.
Do not put the datafile into `input/`, but rather in its own folder with a descriptive name, such as `steady-dataset/`. You can specify
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