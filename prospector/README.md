# Prospector

:warning: **WARNING** Prospector is a research prototype,
currently under development: the instructions below are intended for development, testing and demonstration purposes only!

## Description

Prospector is a tool to reduce the effort needed to find security fixes for
*known* vulnerabilities in open source software repositories

It takes a vulnerability description (in natural language) in input and
produces in output a ranked list of commits, in decreasing order of relevance.

If you find a bug, please open an issue. If you can also fix the bug, please
create a pull request (make sure it includes a test case that passes with your correction
but fails without it)


## Setup

:exclamation: Please note that **Windows is not supported** while WSL and WSL2 are fine.

Prerequisites:

* Python 3.10
* postgresql
* gcc g++ libffi-dev python3-dev libpq-dev (to build python dependencies)

The easiest way to set up Prospector is to clone the project KB repository and then navigate to the prospector folder:

```
git clone https://github.com/sap/project-kb
cd project-kb/prospector
```

You can setup everything and install the dependencies by running:
```
make setup
```
or (for development purposes):
```
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


:exclamation: **IMPORTANT**: this project adopts `black` for code formatting. You may want to configure
your editor so that autoformatting is enforced "on save". The pre-commit hook ensures that
black is run prior to committing anyway, but the auto-formatting might save you some time
and avoid frustration.

If you use VSCode, this can be achieved by pasting these lines in your configuration file:

```
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
```

## Starting the backend database and the job workers [OPTIONAL]

If you run the client without running the backend you will get a warning and have slower response times when making multiple queries. If you only intend to try out the client, feel free to skip this section and the next and go straight to "Using the CLI".

Note: this section and the following assume you have performed succesfully the
steps in the *setup* section above.

This is achieved with docker and docker-compose, make sure you have both installed
and working before proceeding.

You can then start the necessary containers with the following command:

`make docker-setup`

This also starts a convenient DB administration tool at http://localhost:8080

If you wish to cleanup docker to run a fresh version of the backend you can run:

`make docker-clean`

## Starting the RESTful server

`uvicorn api.main:app --reload`

Note, that it requires `POSTGRES_USER`, `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DBNAME` to be set in the .env file.

You can then point your browser to `http://127.0.0.1:8000` to access the API.
You might also want to take a look at `http://127.0.0.1:8000/docs`.

*Alternatively*, you can execute the RESTful server explicitly with:

`python api/main.py`

which is equivalent but more convenient for debugging.


## Using the CLI

Try the following example:

`python client/cli/main.py CVE-2014-0050 --repository https://github.com/apache/commons-fileupload --use-nvd`

or, specifying the tag interval to restrict the retrieval of candidate commits:

`python client/cli/main.py CVE-2014-0050 --repository https://github.com/apache/commons-fileupload --use-nvd --tag-interval FILEUPLOAD_1_3:FILEUPLOAD_1_3_1`

In the example above, the tag interval has been chosen by considering the text of the advisory ("MultipartStream.java in Apache Commons FileUpload before 1.3.1 [...]") and comparing it with the set of tags found  in the git repository.

*HEADS-UP*: Prospector has the capability to "guess" tag names from version intervals, but that functionality is not yet exposed to the command line client (it will be in the future). If you are curious to know how that works, please see the last page of [this paper](https://arxiv.org/pdf/2103.13375).

## Testing

Prospector makes use of `pytest`.

:exclamation: **NOTE:** before using it please make sure to have running instances of the backend and the database.

## History

The high-level structure of Prospector follows the approach of its
predecessor FixFinder, which is described in detail here: https://arxiv.org/pdf/2103.13375.pdf

FixFinder is the prototype developed by Daan Hommersom as part of his thesis
done in partial fulfillment of the requirements for the degree of Master of
Science in Data Science & Entrepreneurship at the Jheronimus Academy of Data
Science during a graduation internship at SAP.

The main difference between FixFinder and Prospector (which has been implemented from scratch)
is that the former takes a definite data-driven approach and trains a ML model to perform the ranking,
whereas the latter applies hand-crafted rules to assign a relevance score to each candidate commit.

The document that describes FixFinder can be cited as follows:

@misc{hommersom2021mapping,
    title = {Automated Mapping of Vulnerability Advisories onto their Fix Commits in Open Source Repositories},
    author = {Hommersom, Daan and
    Sabetta, Antonino and
    Coppola, Bonaventura and
    Dario Di Nucci and
    Tamburri, Damian A. },
    year = {2021},
    month = {March},
    url = {https://arxiv.org/pdf/2103.13375.pdf}
}
