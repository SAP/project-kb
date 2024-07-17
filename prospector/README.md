# Prospector

:warning: **WARNING** Prospector is a research prototype,
currently under development: the instructions below are intended for development, testing and demonstration purposes only!

:exclamation: Please note that **Windows is not supported** while WSL and WSL2 are fine.

## Table of Contents

1. [Description](#description)
2. [Quick Setup & Run](#setup--run)
3. [Development Setup](#development-setup)
4. [Contributing](#contributing)
5. [History](#history)

## 📖 Description

Prospector is a tool to reduce the effort needed to find security fixes for
*known* vulnerabilities in open source software repositories.

Given an advisory expressed in natural language, Prospector processes the commits found in the target source code repository, ranks them based on a set of predefined rules, and produces a report that the user can inspect to determine which commits to retain as the actual fix.

## ⚡️ Quick Setup & Run

Prerequisites:

* Docker (make sure you have Docker installed and running before proceeding with the setup)
* Docker-compose

To quickly set up Prospector, follow these steps. This will run Prospector in its containerised version. If you wish to debug or run Prospector's components individually, follow the steps below at [Development Setup](#development-setup).

1. Clone the project KB repository
    ```
    git clone https://github.com/sap/project-kb
    ```
2. Navigate to the *prospector* folder
    ```
    cd project-kb/prospector
    ```
3. Rename the *config-sample.yaml* file in *config.yaml*. <br> Optionally adjust settings such as backend usage, NVD database preference, report format, and more.
    ```
    mv config-sample.yaml config.yaml
    ```
   Note: If you want to use the backend, make sure you set the `POSTGRES_DATA` variable in your `.env` to point to a local directory to save the backend data to. This ensures that the database can persist, even if the docker containers are stopped.

4. Execute the bash script *run_prospector.sh* specifying the *-h* flag. <br> This will display a list of options that you can use to customize the execution of Prospector.
    ```
    ./run_prospector.sh -h
    ```
    The bash script builds and starts the required Docker containers. Once the building step is completed, the script will show the list of available options.

5. Try the following example:
    ```
    ./run_prospector.sh CVE-2020-1925 --repository https://github.com/apache/olingo-odata4
    ```
    By default, Prospector saves the results in a HTML file named *prospector-report.html*.
    Open this file in a web browser to view what Prospector was able to find!


### 🤖 LLM Support

To use Prospector with LLM support, you simply set required parameters for the API access to the LLM in *config.yaml*. These parameters can vary depending on your choice of provider, please follow what fits your needs (drop-downs below). If you do not want to use LLM support, keep the `llm_service` block in your *config.yaml* file commented out.

<details><summary><b>Use SAP AI CORE SDK</b></summary>

You will need the following parameters in *config.yaml*:

```yaml
llm_service:
    type: sap
    model_name: <model_name>
    temperature: 0.0
    ai_core_sk: <file_path>
```

`<model_name>` refers to the model names available in the Generative AI Hub in SAP AI Core. You can find an overview of available models on the Generative AI Hub GitHub page.

In `.env`, you must set the deployment URL as an environment variable following this naming convention:
```yaml
<model_name>_URL  # model name in capitals, and "-" changed to "_"
```
For example, for gpt-4's deployment URL, set an environment variable called `GPT_4_URL`.

The `temperature` parameter is optional. The default value is 0.0, but you can change it to something else.

You also need to point the `ai_core_sk` parameter to a file contianing the secret keys.

</details>

<details><summary><b>Use personal third party provider</b></summary>

Implemented third party providers are **OpenAI**, **Google**, **Mistral**, and **Anthropic**.

1. You will need the following parameters in *config.yaml*:
    ```yaml
    llm_service:
        type: third_party
        model_name: <model_name>
        temperature: 0.0
    ```

    `<model_name>` refers to the model names available, for example `gpt-4o` for OpenAI. You can find a lists of available models here:
   1. [OpenAI](https://platform.openai.com/docs/models)
   2. [Google](https://ai.google.dev/gemini-api/docs/models/gemini)
   3. [Mistral](https://docs.mistral.ai/getting-started/models/)
   4. [Anthropic](https://docs.anthropic.com/en/docs/about-claude/models)

    The `temperature` parameter is optional. The default value is 0.0, but you can change it to something else.

2. Make sure to add your OpenAI API key to your `.env` file as `[OPENAI|GOOGLE|MISTRAL|ANTHROPIC]_API_KEY`.

</details>

#### How to use LLM Support for different things

You can set the `use_llm_<...>` parameters in *config.yaml* for fine-grained control over LLM support in various aspects of Prospector's phases. Each `use_llm_<...>` parameter allows you to enable or disable LLM support for a specific aspect:

- **`use_llm_repository_url`**: Choose whether LLMs should be used to obtain the repository URL. When using this option, you can omit the `--repository` flag as a command line argument and run prospector with `./run_prospector.sh CVE-2020-1925`.


## 👩‍💻 Development Setup

Following these steps allows you to run Prospector's components individually: [Backend database and worker containers](#starting-the-backend-database-and-the-job-workers), [RESTful Server](#starting-the-restful-server) for API endpoints, [Prospector CLI](#running-the-cli-version) and [Tests](#testing).

If you have issues with these steps, please open a Github issue and
explain in detail what you did and what unexpected behaviour you observed
(also indicate your operating system and Python version).

**Prerequisites:**

* Python 3.10
* postgreSQL
* gcc g++ libffi-dev python3-dev libpq-dev
* Docker & Docker-compose

### General

You can setup everything and install the dependencies by running:
```
make setup
make dev-setup
```

This is necessary only the first time you set up your dev. environment.

Afterwards, you will just have to set the environment variables using the `.env` file and sourcing it with:

```
set -a; source .env; set +a
```

You can configure prospector from CLI or from the *config.yaml* file. The (recommended) API Keys for Github and the NVD can be configured from the `.env` file (which must then be sourced with `set -a; source .env; set +a`)

#### Requirements

If at any time you wish to use a different version of the python interpreter, beware that the `requirements.txt` file contains the exact versioning for `python 3.10.6`.

If you need to update the requirements, add the packages to `requirements.in`. Then recompile `requirements.txt` with `pip-cmpile --no-annotate --strip-extras` (You'll need to have pip-tools installed: `python3 -m pip install pip-tools`). If `requirements.txt` gets generated with `pip extra`'s at the top, remove these before you push (as this will make the build try to fetch them for hours).

#### Code Formatting

:exclamation: **IMPORTANT**: this project adopts `black` for code formatting. You may want to configure
your editor so that autoformatting is enforced "on save". The pre-commit hook ensures that
black is run prior to committing anyway, but the auto-formatting might save you some time
and avoid frustration.

If you use VSCode, this can be achieved by installing the Black Formatter extension and pasting these lines in your configuration file:

```json
    "[python]": {
        "editor.defaultFormatter": "ms-python.black-formatter",
        "editor.formatOnSave": true,
    }
```

### Starting the backend database and the job workers

If you run the client without running the backend you will get a warning and have slower response times when making multiple queries.

You can then start the necessary containers with the following command:

```bash
make docker-setup
```

This also starts a convenient DB administration tool at http://localhost:8080. Also, make sure you have set your `POSTGRES_DATA` environment
variable in `.env`. It should point to a local folder to where the database data can be saved to, in order for the database to persist,
even if the containers are stopped. If you want to delete the existing database (eg. because changes to the schema have been made), attach
to the db docker container `db` in interactive mode by running:

```bash
docker exec -it db bash
```

Then navigate to the folder containing the database data: `/var/lib/postgresql/data/` and empty it with:

```bash
$/var/lib/postgresql/data/ rm -rf *
```

This needs to be done before stopping and restarting the containers: The `db` container will not execute any scripts if the `/var/lib/postgresql/data/` folder
is not empty and therefore not create a new database, even if you cleanup docker with the command below.

If you wish to cleanup docker to run a fresh version of the backend you can run:

```bash
make docker-clean
```

### Starting the RESTful server

```bash
uvicorn service.main:app --reload
```

Note, that it requires `POSTGRES_USER`, `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DBNAME` to be set in the .env file.

You can then point your browser to `http://127.0.0.1:8000` to access the API.
You might also want to take a look at `http://127.0.0.1:8000/docs`.

*Alternatively*, you can execute the RESTful server explicitly with:

```bash
python api/main.py
```

which is equivalent but more convenient for debugging.

### Running the CLI version

The script `run_prospector.sh` also containerize the CLI version of the tool. To execute Prospector outside of the docker container run `python cli/main.py`

### Testing

Prospector makes use of `pytest`.

:exclamation: **NOTE:** before using it please make sure to have running instances of the backend and the database.

## 🤝 Contributing

If you find a bug, please open an issue. If you can also fix the bug, please
create a pull request (make sure it includes a test case that passes with your correction
but fails without it)

## 🕰️ History

The high-level structure of Prospector follows the approach of its
predecessor FixFinder, which is described in:

> Daan Hommersom, Antonino Sabetta, Bonaventura Coppola, Dario Di Nucci, and Damian A. Tamburri. 2024. Automated Mapping of Vulnerability Advisories onto their Fix Commits in Open Source Repositories. ACM Trans. Softw. Eng. Methodol. March 2024. https://doi.org/10.1145/3649590

FixFinder is the prototype developed by Daan Hommersom as part of his thesis
done in partial fulfillment of the requirements for the degree of Master of
Science in Data Science & Entrepreneurship at the Jheronimus Academy of Data
Science during a graduation internship at SAP.

The source code of FixFinder can be obtained by checking out the tag [DAAN_HOMMERSOM_THESIS](https://github.com/SAP/project-kb/releases/tag/DAAN_HOMMERSOM_THESIS).

The main difference between FixFinder and Prospector (which has been implemented from scratch)
is that the former takes a definite data-driven approach and trains a ML model to perform the ranking,
whereas the latter is based on hand-crafted rules to assign a relevance score to each candidate commit.

Recent versions of Prospector (2024) also use AI/ML; still that is done through suitable rules
that are based on the outcome of suitable requests to LLMs.

The paper that describes FixFinder can be cited as follows:

@article{10.1145/3649590,
author = {Hommersom, Daan and Sabetta, Antonino and Coppola, Bonaventura and Nucci, Dario Di and Tamburri, Damian A.},
title = {Automated Mapping of Vulnerability Advisories onto their Fix Commits in Open Source Repositories},
year = {2024},
publisher = {Association for Computing Machinery},
address = {New York, NY, USA},
issn = {1049-331X},
url = {https://doi.org/10.1145/3649590},
doi = {10.1145/3649590},
journal = {ACM Trans. Softw. Eng. Methodol.},
month = {mar},
}
