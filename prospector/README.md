# Prospector

## What is it
Prospector is a tool to reduce the effort needed to find security fixes for
*known* vulnerabilities in open source software repositories.

Prospector takes a vulnerability description (in natural language) as input and
produces an annotated list of candidate commits, where the annotations mark the
commits that match certain criteria. These criteria are implemented as rules
that inspect the attributes of the advisory object and those of the candidate
commits.

The development of this new version is funded by EU grant number 952647
([AssureMOSS](https://assuremoss.eu/en/)).

<p align="center">
    <a href="https://assuremoss.eu">
        <img height="120" src="docs/img/assuremoss_logo.png">
    </a>
</p>


**WARNING** Please keep in mind that Prospector is a research prototype,
currently under development: feel free to try it out, but do expect some rough
edges.

If you find an bug, please open an issue. I you can also fix the bug, please
create a pull request (make sure it includes a test case that passes with your
correction but fails without it)

Prospector is a complete re-implementation of a previous prototype (see *prospector-alpha* below) developed by SAP Security Research intern Daan Hommersom.


## Setup (for development, testing, and demonstration purposes only!)

The easiest way to set up Prospector is to clone this repository and then run
the following commands:

```
git clone https://github.com/sap/project-kb
git checkout prospector-assuremoss
cd project-kb/prospector
cp .env-sample .env
```

Modify the `.env` file to match your setup, then continue with:

```
source .env
mkdir -p $GIT_CACHE
pipenv --python 3.8
pipenv install --dev
pre-commit install
python -m spacy download en_core_web_sm
```

If at any time you wish to remove the virtual environment and create it from scratch
(for example, because you want to use a different version of the python interpreter),
just do `pipenv --rm` and the repeat the steps above.

If you have issues with these steps, please open a Github issue and
explain in detail what you did and what unexpected behaviour you observed
(also indicate your operating system and Python version).

*Please note that Windows is not supported*. WSL should work, though.


**IMPORTANT**: this project adopts `black` for code formatting. You may want to configure
your editor so that autoformatting is enforced "on save". The pre-commit hook ensures that
black is run prior to committing anyway, but the auto-formatting might save you some time
and avoid frustration.

If you use VScode, this can be achieved by pasting these lines in your configuration file:

```
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
```

## Testing

To run the unit tests, run:

`pytest`

NOTE: some tests might require the backend components (RESTful API server, database, workers)
to be running. See the section below for details.


## Starting the backend database and the job workers

THIS STEP IS OPTIONAL: if the client is invoked but the backend is not running,
you will just get a warning and miss out on opportunities to have faster response times
if you make multiple queries. If you only intend to try out the client, feel free to skip
this section and the next and go straight to "Using the CLI".

Note: this section and the following assume you have performed succesfully the
steps in the *setup* section above.

This is achieved with docker and docker-compose, make sure you have both installed
and working before proceeding.

You can then start the necessary containers with the following command:

`docker-compose up -d --build`

This also starts a convenient DB administration tool at http://localhost:8080


## Starting the RESTful server only

The docker-compose command above also starts the backend. The following is only
needed if you want to start the backend but not the rest of the components, for example
if you are developing the backend or if you want to debug or test it.

You use the following command:

`uvicorn api.main:app --reload`

You can then point your browser to `http://127.0.0.1:8000` to access the API.
You might also want to take a look at `http://127.0.0.1:8000/docs`.

*Alternatively*, you can execute the RESTful server explicitly with:

`python api/main.py`

which is equivalent but, depending on your development environment, it could be
more convenient for debugging.

## Using the CLI

Try the following example:

`python client/cli/main.py CVE-2014-0050 --repository https://github.com/apache/commons-fileupload --use-nvd`

or, specifying the tag interval to restrict the retrieval of candidate commits:

`python client/cli/main.py CVE-2014-0050 --repository https://github.com/apache/commons-fileupload --use-nvd --tag-interval FILEUPLOAD_1_3:FILEUPLOAD_1_3_1`

In the example above, the tag interval has been chosen by considering the text
of the advisory ("MultipartStream.java in Apache Commons FileUpload before 1.3.1
[...]") and comparing it with the set of tags found  in the git repository.




## Prior versions of this tool (Prospector-alpha)

This is a complete *reimplementation* of an earlier research prototype that we
now refer to as `prospector-alpha`. The goals of prospector-alpha were similar,
but the emphasis was more on building a completely automated (non-interactive)
tool, whereas the new implementation aims at supporting the user by automating
parts of the mining process (the more repetitive, time-consuming, error-prone)
but leaving to them the ultimate selection of fix-commits. The techniques used
in the two implementations are radically different. Prospector-alpha strongly
relies on ML learning to rank candidate commits and its models were trained on
the project KB data, whereas the new implementation is focussing on implementing
a set of rules that mimick the mining methods that a human expert would use. The
advantages of the latter approach are better performance, explainability of
results, and effectiveness. Furthermore, we plan to introduce ML in the new
implementation as well to complement the rule-based processing and to prioritise
candidates.

Prospector-alpha was implemented by Daan Hommersom during his internship at SAP
Security Research for his Master thesis in Data Science & Entrepreneurship at
the Jheronimus Academy of Data Science (JADS).

The original code developed by Daan Hommersom can be retrieved
[here](https://github.com/SAP/project-kb/tree/DAAN_HOMMERSOM_THESIS/prospector).


The approach implemented in Prospector-alpha is described in detail in this
document: https://arxiv.org/pdf/2103.13375.pdf

The document can be cited as follows:

@misc{hommersom2021mapping,
    title = {Automated Mapping of Vulnerability Advisories onto their Fix Commits in Open Source Repositories},
    author = {Hommersom, Daan and
    Sabetta, Antonino and
    Coppola, Bonaventura and
    Tamburri, Damian A. },
    year = {2021},
    month = {March},
    url = {https://arxiv.org/pdf/2103.13375.pdf}
}
