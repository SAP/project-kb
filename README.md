# project "KB"

[![Go Report Card](https://goreportcard.com/badge/github.com/sap/project-kb)](https://goreportcard.com/report/github.com/sap/project-kb)
[![Go](https://github.com/sap/project-kb/workflows/Go/badge.svg)](https://github.com/SAP/project-kb/actions?query=workflow%3AGo)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/SAP/project-kb/blob/master/LICENSE.txt)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/sap/project-kb/#contributing)
[![Join the chat at https://gitter.im/project-kb/general](https://badges.gitter.im/project-kb/general.svg)](https://gitter.im/project-kb/general?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
![GitHub All Releases](https://img.shields.io/github/downloads/SAP/PROJECT-KB/total)
[![REUSE status](https://api.reuse.software/badge/github.com/sap/project-kb)](https://api.reuse.software/info/github.com/sap/project-kb)
[![Pytest](https://github.com/SAP/project-kb/actions/workflows/python.yml/badge.svg)](https://github.com/SAP/project-kb/actions/workflows/python.yml)


The goal of `Project KB` is to enable the creation, management and aggregation of a
distributed, collaborative knowledge base of vulnerabilities that affect
open-source software.

`Project KB` consists of vulnerability data [vulnerability knowledge-base](vulnerability-data)
as well as set of tools to support the mining, curation and management of such data.


## Why this project

In order to feed [Eclipse Steady](https://github.com/eclipse/steady/) with fresh
data, we have spent a considerable amount of time, in the past few years, mining
and curating a knowledge base of vulnerabilities that affect open-source
components. We know that other parties have been doing the same, in academia as
well as in the industry. From this experience, we have learnt that with the
growing size of open source ecosystems and the pace at which new vulnerabilities
are discovered, the _old approach_ cannot scale. We are also more and more
convinced that vulnerability knowledge-bases about open-source should be
open-source themselves and adopt the same community-oriented model that governs
the rest of the open-source ecosystem.

These considerations have pushed us to release our vulnerability knowledge base
in early 2019. In June 2020, we made a further step releasing the `kaybee` tool support to
make the creation, aggregation, and consumption of vulnerability data much
easier. In late 2020, we also released, as a proof-of-concept, the prototype
`prospector`, whose goal is to automate the mapping of vulnerability advisories
onto their fix-commits. A technical description of the approach we implemented in
`prospector` can be found in this [preprint](https://arxiv.org/abs/2103.13375).
As of April 2021, together with our partners in the EU-funded project AssureMOSS,
we are reimplementing `prospector` to make it more robust, scalable, and user-friendly.
The reimplementation is carried out in the dedicate branch `prospector-assuremoss`.

We hope this will encourage more contributors to join our efforts to build a
collaborative, comprehensive knowledge base where each party remains in control
of the data they produce and of how they aggregate and consume data from the
other sources.


### What can project "KB" be used for, in practice

(work in progress)

Project "KB" consists essentially of two things: a toolkit and a knowledge base.

The **toolkit** comprises:

  * `kaybee`, a tool to:
    - create vulnerability statements; a vulnerability statement is a plain-text file in yaml format
      that contains data about a given vulnerability, such as the commits that provide a fix for it,
      a set of notes and references to related Web pages, a list of open-source components that
      are directly affected by the vulnerability at hand, and so on.
    - fetch vulnerability statements from one or more remote sources (git repositories)
    - merge the content of multiple sources of statements, based on a conflict resolution policy
    - export the result of the merge operation to a variety of different formats
  * `prospector`, a research prototype to help map vulnerability advisories onto the commits that contain fixes for those vulnerabilities.

The **knowledge base**, offers a set of vulnerability statements that can be consumed using the `kaybee` tool.




## Project KB in a nutshell

### Vulnerability data

The vulnerability data of Project KB are stored in textual form as a set of YAML files, in branch `vulnerability-data`.

### Tools

#### Vulnerability Data Management: `kaybee`

With `kaybee` it is possible to fetch the vulnerability statements from this
repository (or from any other repository) and export them to a number of
formats, including a script to import them to a [Steady
backend](https://github.com/eclipse/steady).

See https://github.com/SAP/project-kb/tree/main/kaybee for details. 

#### Vulnerability Data Mining Tool: `prospector`

Prospector is a tool to reduce the effort needed to find security fixes for known vulnerabilities in open source software repositories.
The tool takes a vulnerability description (in natural language) as input and produces a ranked list of commits, in decreasing order of relevance.

See https://github.com/SAP/project-kb/tree/main/prospector for details.

## Publications

In early 2019, a snapshot of the knowlege base from project "KB" was described in:

  - Serena E. Ponta, Henrik Plate, Antonino Sabetta, Michele Bezzi, Cédric
    Dangremont, [A Manually-Curated Dataset of Fixes to Vulnerabilities of
    Open-Source Software](http://arxiv.org/abs/1902.02595), MSR, 2019

If you use the dataset for your research work, please cite it as:

```
@inproceedings{ponta2019msr,
    author={Serena E. Ponta and Henrik Plate and Antonino Sabetta and Michele Bezzi and
    C´edric Dangremont},
    title={A Manually-Curated Dataset of Fixes to Vulnerabilities of Open-Source Software},
    booktitle={Proceedings of the 16th International Conference on Mining Software Repositories},
    year=2019,
    month=May,
}
```

**MSR 2019 DATA SHOWCASE SUBMISSION**: please find [here the data and the
scripts described in that paper](MSR2019)

> If you wrote a paper that uses the data or the tools from this repository, please let us know (through an issue) and we'll add it to this list.

## Credits

### EU-funded research projects

The development of Project KB is partly supported by the following EU-funded projects:

* [AssureMOSS](https://assuremoss.eu) (Grant No.952647).
* [Sparta](https://www.sparta.eu/) (Grant No.830892).


### 3rd party vulnerability data sources

3rd party information from NVD and MITRE might have been used as input
for compiling parts of this knowledge base. See MITRE's [Terms of
Use](http://cve.mitre.org/about/termsofuse.html) for more information.
See also [this notice](NOTICE.txt).

## Requirements

See the README files for `kaybee` and `prospector`.

## Limitations and Known Issues

This project is work-in-progress. The vulnerability knowledge base only contains
information about vulnerabilities in Java and Python open source components.

The list of current issues is available
[here](https://github.com/SAP/project-kb/issues).

Feel free to open a new issue if you think you found a bug or if you have a feature request.

## How to obtain support

For the time being, please use [GitHub
issues](https://github.com/SAP/project-kb/issues) both to report bugs and to
request help. Documentation and better support channels will come soon.

## Contributing

See [here](CONTRIBUTING.md).
