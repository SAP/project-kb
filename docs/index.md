# project "KB"

[![Go Report Card](https://goreportcard.com/badge/github.com/sap/project-kb)](https://goreportcard.com/report/github.com/sap/project-kb)
![Go](https://github.com/sap/project-kb/workflows/Go/badge.svg)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/SAP/project-kb/blob/master/LICENSE.txt)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](contributing)
![GitHub All Releases](https://img.shields.io/github/downloads/SAP/PROJECT-KB/total)
[![REUSE status](https://api.reuse.software/badge/github.com/sap/project-kb)](https://api.reuse.software/info/github.com/sap/project-kb)
[![Join the chat at https://gitter.im/project-kb/help](https://badges.gitter.im/project-kb/help.svg)](https://gitter.im/project-kb/help?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

The goal of `Project KB` is to enable the creation, management and aggregation of a
distributed, collaborative knowledge base of vulnerabilities affecting
open-source software.

`Project KB` consists of [vulnerability data](https://github.com/SAP/project-kb/tree/main/vulnerability-data)
as well as set of tools to support the mining, curation and management of such data.

## Available Tools
<div style="text-align: center;">
 <div style="display: inline-block; margin-right: 20px;">
  <a href="kaybee" class="md-button md-button--primary">Kaybee</a>
 </div>
 <div style="display: inline-block;">
  <a href="prospector" class="md-button md-button--primary">Prospector</a>
 </div>
</div>

### Kaybee

KayBee is a vulnerability data management tool, it makes possible to fetch the vulnerability statements from this
repository (or from any other repository) and export them to a number of
formats, including a script to import them to a [Steady
backend](https://github.com/eclipse/steady).

### Prospector

Prospector is a vulnerability data mining tool that aims at reducing the effort needed to find security fixes for known vulnerabilities in open source software repositories.

Given a vulnerability advisory and a software repository, it
analyses them to produce a report in which commits are ranked
according to the likelihood that they fix the vulnerability.

## Vulnerability data

The vulnerability data of Project KB are stored in textual form as a set of YAML files, in the [vulnerability-data branch](https://github.com/SAP/project-kb/tree/vulnerability-data).

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

The development of Project KB is partially supported by the following projects:

* [AssureMOSS](https://assuremoss.eu) (Grant No.952647).
* [Sparta](https://www.sparta.eu/) (Grant No.830892).

### Vulnerability data sources

Vulnerability information from NVD and MITRE might have been used as input
for building parts of this knowledge base. See MITRE's [CVE Usage license](http://cve.mitre.org/about/termsofuse.html) for more information.

## Limitations and Known Issues

This project is **work-in-progress**, you can find the list of known issues [here](https://github.com/SAP/project-kb/issues).

Currently the vulnerability knowledge base only contains information about vulnerabilities in Java and Python open source components.

## Support

For the time being, please use [GitHub
issues](https://github.com/SAP/project-kb/issues) to report bugs, request new features and ask for support.

## Contributing

See [How to contribute](contributing.md).
