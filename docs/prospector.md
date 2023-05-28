# Prospector

???+ note
    Prospector is a research prototype,
    currently under development: the instructions below are intended for development, testing and demonstration purposes only!

    :exclamation: Please note that **Windows is not supported** while WSL and WSL2 are fine.

Prospector is a tool to reduce the effort needed to find security fixes for
*known* vulnerabilities in open source software repositories.

Given an advisory expressed in natural language, Prospector processes the commits found in the target source code repository, ranks them based on a set of predefined rules, and produces a report that the user can inspect to determine which commits to retain as the actual fix.

## Setup & Run

???+ warning
    The tool requires Docker and Docker-compose, as it employes Docker containers for certain functionalities. Make sure you have Docker installed and running before proceeding with the setup and usage of Prospector.

To quickly set up Prospector:

1. Clone the project KB repository
```
git clone https://github.com/sap/project-kb
```
2. Navigate to the *prospector* folder
```
cd project-kb/prospector
```

3. Execute the bash script *run_prospector.sh* specifying the *-h* flag. This will display a list of options that you can use to customize the execution of Prospector.
```
./run_prospector.sh -h
```
The bash script builds and starts the required Docker containers. Once the building step is completed, the script will show the list of available options.

4. Try the following example:
```
./run_prospector.sh CVE-2020-1925 --repository https://github.com/apache/olingo-odata4
```

By default, Prospector saves the results in a HTML file named *prospector-report.html*.

???+ success
    Open the *prospector-report.html* file in a web browser to view what Prospector was able to find!

## Tool Demostration

### Video Recording
<iframe width="560" height="315" src="https://www.youtube.com/<IDHERE>" frameborder="0" allowfullscreen></iframe>

A video recording of the tool demo is also available [here](https://zenodo.org/record/7974442)

### Outline of the Demo
The steps shown in the video are the following:

1. Cloning the [project “KB”](https://github.com/SAP/project-kb) GitHub repository
2.  Execution of the script *run_prospector.sh* from the *prospector* subfolder. The script automatically builds and starts all the necessary docker containers
3.  The command line flags are shown on the screen; for the demo, we use the strictly
required inputs only, which are: *(A)* a vulnerability identifier and *(B)* the URL of the source code
repository of the project affected by the vulnerability
4. As illustrative example, Prospector is executed on *CVE-2020-1925* and the *Apache Olingo*
repository. As the tool runs, we give a high-level explanation of the processing it performs
(advisory record extraction, candidate commits retrieval and processing, rule application, report
generation).
5. The report generated at the end of the previous step is shown and its key elements are
described.
6. We highlight the fact that the advisory content is processed to extract important tokens
(keywords, file names, etc.).
7. We explain that commits are ranked by their relevance, which is computed by applying a
set of rules to each of them. The sum of the weights of the rules that match a commit determine
its relevance. The list of commits shown in the report can be filtered by a applying a relevance
threshold using a slider.
8. As a concrete example, we point out that the tool detected that the first commit in the list
modifies a class that is mentioned in the textual description of the advisory.

## Contributing
* [How to contribute](contributing.md)
