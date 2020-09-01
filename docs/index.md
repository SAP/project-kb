# project "KB"

[![Go Report Card](https://goreportcard.com/badge/github.com/sap/project-kb)](https://goreportcard.com/report/github.com/sap/project-kb)
![Go](https://github.com/sap/project-kb/workflows/Go/badge.svg)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/SAP/project-kb/blob/master/LICENSE.txt)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](contributing)
![GitHub All Releases](https://img.shields.io/github/downloads/SAP/PROJECT-KB/total)
[![REUSE status](https://api.reuse.software/badge/github.com/sap/project-kb)](https://api.reuse.software/info/github.com/sap/project-kb)
[![Join the chat at https://gitter.im/project-kb/help](https://badges.gitter.im/project-kb/help.svg)](https://gitter.im/project-kb/help?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

`project KB` supports the creation, management and aggregation of a
distributed, collaborative knowledge base of vulnerabilities that affect
open-source software.

This repository contains both a [tool](kaybee) and [vulnerability data](https://github.com/SAP/project-kb/tree/master/vulnerability-data).

Additionally, the [MSR2019](https://github.com/SAP/project-kb/tree/master/MSR2019) folder contains the package associated with
the paper we published at the Mining Software Repository conference in 2019 (see
below).

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
in early 2019. In June 2020, we made a further step releasing tool support to
make the creation, aggregation, and consumption of vulnerability data much
easier.

We hope this will encourage more contributors to join our efforts to build a
collaborative, comprehensive knowledge base where each party remains in control
of the data they produce and of how they aggregate and consume data from the
other sources.

### What can project "KB" be used for, in practice

(work in progress)

Project "KB" consists essentially of two things: a tool and a knowledge base.

The **tool** (`kaybee`) allows users to do the following:

- create vulnerability statements; a vulnerability statement is a plain-text file in yaml format
  that contains data about a given vulnerability, such as the commits that provide a fix for it,
  a set of notes and references to related Web pages, a list of open-source components that
  are directly affected by the vulnerability at hand, and so on.
- fetch vulnerability statements from one or more remote sources (git repositories)
- merge the content of multiple sources of statements, based on a conflict resolution policy
- export the result of the merge operation to a variety of different formats

The **knowledge base**, offers a set of vulnerability statements that can be consumed using the `kaybee` tool.
It contents are kept in the dedicated branch `vulnerability-data`.

## Getting started

### Installing the `kaybee` tool

### Importing vulnerability data in Eclipse Steady

The steps that are required to import the knowledge base in [Eclipse
Steady](https://github.com/eclipse/steady/) are described in [this
tutorial](https://eclipse.github.io/steady/vuln_db/tutorials/vuln_db_tutorial/).
Further information can be found
[here](https://eclipse.github.io/steady/vuln_db/).

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

## Credits

### Sparta project

The development of Project KB is partly supported by [EU-funded project Sparta](https://www.sparta.eu/).

### 3rd party vulnerability data sources

3rd party information from NVD and MITRE might have been used as input
for compiling parts of this knowledge base. See MITRE's [Terms of
Use](http://cve.mitre.org/about/termsofuse.html) for more information.
See also [this notice](https://github.com/SAP/project-kb/tree/master/NOTICE.txt).


## Features

- Creation of vulnerability statements
- Retrieval and reconciliation of statement from multiple repositories, based on
  user-specified policies

## Requirements

None, the `kaybee` binary is self-contained. Binary versions for Windows, Linux,
MacOS are available for [download](https://github.com/SAP/project-kb/releases).

## Limitations

This project is work-in-progress. The vulnerability knowledge base only contains
information about vulnerabilities in Java and Python open source components.

## Known Issues

The list of current issues is available
[here](https://github.com/SAP/project-kb/issues).

Feel free to open a new issue if you think you found a bug or if you have a
feature request.

## How to obtain support

First, take a look at our documentation.

If you cannot find the answer to your questions, you may want to ask for help
on this [Gitter channel](https://gitter.im/project-kb/help).

If you think you found a bug, please create an [issue](https://github.com/SAP/project-kb/issues).


## License

Copyright (c) 2020 SAP SE or an SAP affiliate company. All rights reserved.

This project is licensed under the Apache Software License, v.2 except as noted
otherwise in the [LICENSE file](https://github.com/SAP/project-kb/blob/master/LICENSE.txt).
