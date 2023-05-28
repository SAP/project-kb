# Development Setup

## Prerequisites

* Python 3.10
* postgreSQL
* gcc g++ libffi-dev python3-dev libpq-dev
* Docker & Docker-compose

## Setup

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

You can configure prospector from CLI or from the `config.yaml` file. The (recommended) API Keys for Github and the NVD can be configured from the `.env` file (which must then be sourced with `set -a; source .env; set +a`)

If at any time you wish to use a different version of the python interpreter, beware that the `requirements.txt` file contains the exact versioning for `python 3.10.6`.

If you have issues with these steps, please open a Github issue and
explain in detail what you did and what unexpected behaviour you observed
(also indicate your operating system and Python version).


???+ tip
    this project adopts `black` for code formatting. You may want to configure
    your editor so that autoformatting is enforced "on save". The pre-commit hook ensures that
    black is run prior to committing anyway, but the auto-formatting might save you some time
    and avoid frustration.

    If you use VSCode, this can be achieved by pasting these lines in your configuration file:

    ```
        "python.formatting.provider": "black",
        "editor.formatOnSave": true,
    ```

### Starting the backend database and the job workers

If you run the client without running the backend you will get a warning and have slower response times when making multiple queries.

You can then start the necessary containers with the following command:

`make docker-setup`

This also starts a convenient DB administration tool at http://localhost:8080

If you wish to cleanup docker to run a fresh version of the backend you can run:

`make docker-clean`

### Starting the RESTful server

`uvicorn api.main:app --reload`

Note, that it requires `POSTGRES_USER`, `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DBNAME` to be set in the .env file.

You can then point your browser to `http://127.0.0.1:8000` to access the API.
You might also want to take a look at `http://127.0.0.1:8000/docs`.

*Alternatively*, you can execute the RESTful server explicitly with:

`python api/main.py`

which is equivalent but more convenient for debugging.

## Running the CLI version

The script `run_prospector.sh` also containerize the CLI version of the tool. To execute Prospector outside of the docker container run `python cli/main.py`

## Testing

Prospector makes use of `pytest`.

???+ note
    before using it please make sure to have running instances of the backend and the database.

## Found a Bug?

If you find a bug, please open an issue. If you can also fix the bug, please
create a pull request (make sure it includes a test case that passes with your correction
but fails without it)

* See [How to contribute](issues.md)
