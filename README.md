<p align="center"><img height="64" src="images/vulas.png"></p>

# Open-source vulnerability assessment knowledge base [![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE.txt) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

The open-source **vulnerability assessment knowledge base** aggregates public information about security vulnerabilities in open source projects, the fuel required to run the [vulnerability assessment tool](https://github.com/SAP/vulnerability-assessment-tool).

The entire knowledge base is contained in file [`dataset.csv`](dataset.csv). Each line of the file contains:

  * A vulnerability identifier (typically a CVE)
  * The URL of the source code repository of the affected open source project
  * A commit fixing the respective vulnerability (which we call *fix commit*)
  
The steps that are required to import the knowledge base into the vulnerability assessment tool are described in [this tutorial](https://sap.github.io/vulnerability-assessment-tool/vuln_db/tutorials/vuln_db_tutorial/). Further information can be found [in the manual](https://sap.github.io/vulnerability-assessment-tool/vuln_db/) of the vulnerability assessment tool.

A more comprehensive description of the dataset and its possible applications (in addition to fueling the vulerability assessment tool) can be found in: 

  - Serena E. Ponta, Henrik Plate, Antonino Sabetta, Michele Bezzi, Cédric Dangremont, [A Manually-Curated Dataset of Fixes to Vulnerabilities of Open-Source Software](http://arxiv.org/abs/1902.02595) (accepted at MSR 2019)

If you use the dataset for your research work, please cite it as:

```
@inproceedings{ponta2019msr,
    author={Serena E. Ponta and Henrik Plate and Antonino Sabetta and Michele Bezzi and
    C´edric Dangremont},
    url={https://arxiv.org/pdf/1902.02595.pdf},
    title={A Manually-Curated Dataset of Fixes to Vulnerabilities of Open-Source Software},
    booktitle={Proceedings of the 16th International Conference on Mining Software Repositories}, 
    year=2019,
    month=May,
}
```

**MSR 2019 DATA SHOWCASE SUBMISSION**: please find [here the data and the scripts described in that paper](MSR2019)

## Motivation

The motivation to open source this dataset is two-fold:

  * First, researchers have access to a manually curated dataset of high quality in order to conduct further research in the areas of software security and software engineering.
  * Second, users of open source components can use this dataset to update and maintain their local instance of the vulnerability assessment tool as to check whether their Java and Python applications are affected by open source vulnerabilities.
  
Eventually, we hope that this knowledge base will be maintained in a collaborative manner.

## Credits

Note that 3rd party information from NVD and MITRE has been used as input for compiling this knowledge base. See MITRE's [Terms of Use](http://cve.mitre.org/about/termsofuse.html) for more information.

## Features

See [here](https://github.com/sap/vulnerability-assessment-tool/#features) to learn about features of the vulnerability assessment tool that become possible due to the dataset available in this knowledge base.

## Requirements

To process the information of the knowledge base, one has to have a running local instance of the vulnerability assessment tool.

Furthermore, you need the **[Java 8 JRE](https://www.oracle.com/technetwork/java/javase/downloads/jre8-downloads-2133155.html)** in order to run the `patch-analyzer` that processes commit information, uploads the analysis results to the `rest-backend`, which eventually stores the data in `PostgreSQL` database. The following image provides an overview about all the involved components. 

<p align="center"><img src="images/components-2.png" height="200"/></p>

## Limitations

As of today, this knowledge base only contains information about vulnerabilities in Java and Python open source components. Even though the vulnerability assessment tool has been designed with extensibility in mind, other programming languages are not yet supported.

## Known Issues

The list of current issues is available [here](https://github.com/SAP/vulnerability-assessment-kb/issues).

## How to obtain support

Use the following link to [Stack Overflow](https://stackoverflow.com/questions/tagged/vulas) to search for FAQs or to request help.

Bug reports shall be submitted as [GitHub issues](https://github.com/SAP/vulnerability-assessment-kb/issues).

## Contributing

Until we have defined a structured process to share the maintenance of the knowledge base, we invite you to just create informal pull requests in order to submit new open source vulnerabilities. Such pull requests should contain a vulnerability identifier, the URL of the source code repository of the affected component and one or more identifiers of the commits used to fix the vulnerability.

## To-Do (upcoming changes)

Process description and tooling to support the shared maintenance of the knowledge base, and to support the automated synchronization of local instances with this GitHub repository.

## License

Copyright (c) 2019 SAP SE or an SAP affiliate company. All rights reserved.

This project is licensed under the Apache Software License, v.2 except as noted otherwise in the [LICENSE file](LICENSE.txt).
