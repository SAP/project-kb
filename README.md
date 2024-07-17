# Project KB

[![Go Report Card](https://goreportcard.com/badge/github.com/sap/project-kb)](https://goreportcard.com/report/github.com/sap/project-kb)
[![Go](https://github.com/sap/project-kb/workflows/Go/badge.svg)](https://github.com/SAP/project-kb/actions?query=workflow%3AGo)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/SAP/project-kb/blob/master/LICENSE.txt)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/sap/project-kb/#contributing)
[![Join the chat at https://gitter.im/project-kb/general](https://badges.gitter.im/project-kb/general.svg)](https://gitter.im/project-kb/general?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
![GitHub All Releases](https://img.shields.io/github/downloads/SAP/PROJECT-KB/total)
[![REUSE status](https://api.reuse.software/badge/github.com/sap/project-kb)](https://api.reuse.software/info/github.com/sap/project-kb)
[![Pytest](https://github.com/SAP/project-kb/actions/workflows/python.yml/badge.svg)](https://github.com/SAP/project-kb/actions/workflows/python.yml)

# Table of contents 
1. [Description](#desc)
2. [Motivations](#motiv)
3. [Kaybee](#kaybee)
4. [Prospector](#prosp)
5. [Vulnerability data](#vuldata)
6. [Publications](#publi)
7. [Star history](#starhist)
8. [Credits](#credit)
9. [EU funded research projects](#eu_funded)
10. [Vulnerability data sources](#vul_data)
11. [Limitations and known issues](#limit)
12. [Support](#support)
13. [Contributing](#contrib)

## Description <a name="desc"></a>

The goal of `Project KB` is to enable the creation, management and aggregation of a
distributed, collaborative knowledge base of vulnerabilities affecting
open-source software.

`Project KB` consists of vulnerability data [vulnerability knowledge-base](vulnerability-data)
as well as set of tools to support the mining, curation and management of such data.


### Motivations <a name="motiv"></a>

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
onto their fix-commits. 

We hope this will encourage more contributors to join our efforts to build a
collaborative, comprehensive knowledge base where each party remains in control
of the data they produce and of how they aggregate and consume data from the
other sources.


## Kaybee <a name="kaybee"></a>

Kaybee is a vulnerability data management tool, it makes possible to fetch the vulnerability statements from this
repository (or from any other repository) and export them to a number of
formats, including a script to import them to a [Steady
backend](https://github.com/eclipse/steady).

For details and usage instructions check out the [kaybee README](https://github.com/SAP/project-kb/tree/main/kaybee).

## Prospector <a name="prosp"></a>

Prospector is a vulnerability data mining tool that aims at reducing the effort needed to find security fixes for known vulnerabilities in open source software repositories.
The tool takes a vulnerability description (in natural language) as input and produces a ranked list of commits, in decreasing order of relevance.

For details and usage instructions check out the [prospector README](https://github.com/SAP/project-kb/tree/main/prospector).

## Vulnerability data <a name="vuldata"></a>

The vulnerability data of Project KB are stored in textual form as a set of YAML files, in the [vulnerability-data branch](https://github.com/SAP/project-kb/tree/vulnerability-data).

## Publications <a name="publi"></a>

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

___

<!-- format :                    Author last name, Initials. (Month Year). [Article title](URL)             -->

**Papers citing our work**
* Bui, Q-C. et al. (May 2022). [Vul4J: a dataset of reproducible Java vulnerabilities geared towards the study of program repair techniques](https://dl.acm.org/doi/abs/10.1145/3524842.3528482)  
* Galvão, P.L. (October 2022). [Analysis and Aggregation of Vulnerability Databases with Code-Level Data](https://repositorio-aberto.up.pt/bitstream/10216/144796/2/588886.pdf)
* Aladics, T. et al.  (2022). [A Vulnerability Introducing Commit Dataset for Java: an Improved SZZ Based Approach](https://real.mtak.hu/149061/1/ICSOFT_2022_41_CR-1.pdf)
* Sharma, T. et al. (October 2021). [A Survey on Machine Learning Techniques for Source Code Analysis](https://arxiv.org/abs/2110.09610)
* Hommersom, D. et al. (June 2024). [Automated Mapping of Vulnerability Advisories onto their Fix Commits in Open Source Repositories](https://dl.acm.org/doi/abs/10.1145/3649590)
* Marchand-Melsom, A. et al. (June 2020). [Automatic repair of OWASP Top 10 security vulnerabilities: A survey](https://dl.acm.org/doi/abs/10.1145/3387940.3392200)
* Sawadogo, A. D. et al. (Dec 2021). [Early Detection of Security-Relevant Bug Reports using Machine Learning: How Far Are We?](https://arxiv.org/abs/2112.10123)
* Sun, S. et al. (Jul 2023). [Exploring Security Commits in Python](https://arxiv.org/abs/2307.11853)
* Reis, S. et al. (June 2021). [Fixing Vulnerabilities Potentially Hinders Maintainability](https://arxiv.org/abs/2106.03271)
* Andrade, R., & Santos, V. (September 2021). [Investigating vulnerability datasets](https://sol.sbc.org.br/index.php/vem/article/view/17213)
* Nguyen, T. G. et al. (May 2023). [Multi-Granularity Detector for Vulnerability Fixesv](https://arxiv.org/abs/2305.13884)
* Siddiq, M. L., & Santos, J. C. S. (November 2022). [SecurityEval dataset: mining vulnerability examples to evaluate machine learning-based code generation techniques](https://dl.acm.org/doi/abs/10.1145/3549035.3561184)
* Sawadogo, A. D. et al. (August 2022). [SSPCatcher: Learning to catch security patches](https://link.springer.com/article/10.1007/s10664-022-10168-9)
* Dunlap, T. et al. (July 2024). [VFCFinder: Pairing Security Advisories and Patches](http://enck.org/pubs/dunlap-asiaccs24.pdf)
* Dunlap, T. et al. (November 2023). [VFCFinder: Seamlessly Pairing Security Advisories and Patches](https://arxiv.org/abs/2311.01532)
* Bao, L. et al. (July 2022). [V-SZZ: automatic identification of version ranges affected by CVE vulnerabilities](https://dl.acm.org/doi/abs/10.1145/3510003.3510113)
* Fan, J. et al. (September 2020). [A C/C++ Code Vulnerability Dataset with Code Changes and CVE Summaries](https://dl.acm.org/doi/abs/10.1145/3379597.3387501)
* Zhang, J. et al. (January 2023). [A Survey of Learning-based Automated Program Repair](https://arxiv.org/abs/2301.03270)
* Alzubaidi, L. et al. (April 2023). [A survey on deep learning tools dealing with data scarcity: definitions, challenges, solutions, tips, and applications](https://link.springer.com/article/10.1186/s40537-023-00727-2)
* Sharma, T. et al. (December 2023). [A survey on machine learning techniques applied to source code](https://www.sciencedirect.com/science/article/pii/S0164121223003291)
* Elder, S. et al. (April 2024). [A Survey on Software Vulnerability Exploitability Assessment](https://dl.acm.org/doi/abs/10.1145/3648610)
* Aladics, T. et al. (March 2023). [An AST-based Code Change Representation and its Performance in Just-in-time Vulnerability Prediction](https://arxiv.org/abs/2303.16591)
* Singhal, A., & Goel, P.K. (2023). [Analysis and Identification of Malicious Mobile Applications](https://ieeexplore.ieee.org/abstract/document/10428519)
* Senanayake, J. et al. (July 2021). [Android Mobile Malware Detection Using Machine Learning: A Systematic Review](https://www.mdpi.com/2079-9292/10/13/1606)
* Bui, Q-C. et al. (December 2023). [APR4Vul: an empirical study of automatic program repair techniques on real-world Java vulnerabilities](https://link.springer.com/article/10.1007/s10664-023-10415-7)
* Senanayake, J. et al. (January 2023). [Android Source Code Vulnerability Detection: A Systematic Literature Review](https://dl.acm.org/doi/full/10.1145/3556974)
* Reis, S. et al. (June 2023). [Are security commit messages informative? Not enough!](https://dl.acm.org/doi/abs/10.1145/3593434.3593481)
* Anonymous authors. (2022). [Beyond syntax trees: learning embeddings of code edits by combining multiple source representations](https://openreview.net/pdf?id=H8qETo_W1-9)
* Challande, A. et al. (April 2022). [Building a Commit-level Dataset of Real-world Vulnerabilities](https://dl.acm.org/doi/abs/10.1145/3508398.3511495)
* Wang, S., & Nagappan, N. (July 2019). [Characterizing and Understanding Software Developer Networks in Security Development](https://arxiv.org/abs/1907.12141)
* Harzevili, N. S. et al. (March 2022). [Characterizing and Understanding Software Security Vulnerabilities in Machine Learning Libraries](https://arxiv.org/abs/2203.06502)
* Tate, S. R. et al. (2020). [Characterizing Vulnerabilities in a Major Linux Distribution](https://home.uncg.edu/cmp/faculty/srtate/pubs/vulnerabilities/Vulnerabilities-SEKE2020.pdf)
* Zhang, L. et al. (January 2023). [Compatible Remediation on Vulnerabilities from Third-Party Libraries for Java Projects](https://arxiv.org/abs/2301.08434)
* Lee, J.Y.D., & Chieu, H.L. (November 2021). [Co-training for Commit Classification](https://aclanthology.org/2021.wnut-1.43/)
* Nikitopoulos, G. et al. (August 2021). [CrossVul: a cross-language vulnerability dataset with commit data](https://dl.acm.org/doi/10.1145/3468264.3473122)
* Bhandari, G.P. (July 2021). [CVEfixes: Automated Collection of Vulnerabilities and Their Fixes from Open-Source Software](https://arxiv.org/abs/2107.08760)
* Sonnekalb, T. et al. (October 2021). [Deep security analysis of program code](https://link.springer.com/article/10.1007/s10664-021-10029-x)
* Triet, H.M. et al. (August 2021). [DeepCVA: Automated Commit-level Vulnerability Assessment with Deep Multi-task Learning](https://arxiv.org/abs/2108.08041)
* Senanayake, J. et al. (May 2024). [Defendroid: Real-time Android code vulnerability detection via blockchain federated neural network with XAI](https://www.sciencedirect.com/science/article/pii/S2214212624000449)
* Stefanoni, A. et al. (2022). [Detecting Security Patches in Java Projects Using NLP Technology](https://aclanthology.org/2022.icnlsp-1.6.pdf)
* Okutan, A. et al. (May 2023). [Empirical Validation of Automated Vulnerability Curation and Characterization](https://s2e-lab.github.io/preprints/tse23-preprint.pdf)
* Wang, J. et al. (October 2023). [Enhancing Large Language Models for Secure Code Generation: A Dataset-driven Study on Vulnerability Mitigation](https://arxiv.org/abs/2310.16263)
* Bottner, L. et al. (December 2023). [Evaluation of Free and Open Source Tools for Automated Software Composition Analysis](https://dl.acm.org/doi/abs/10.1145/3631204.3631862)
* Ganz, T. et al. (November 2021). [Explaining Graph Neural Networks for Vulnerability Discovery](https://dl.acm.org/doi/abs/10.1145/3474369.3486866)
* Ram, A. et al. (November 2019). [Exploiting Token and Path-based Representations of Code for Identifying Security-Relevant Commits](https://arxiv.org/abs/1911.07620)
* Md. Mostafizer Rahman, et al. (July 2023). [Exploring Automated Code Evaluation Systems and Resources for Code Analysis: A Comprehensive Survey](https://arxiv.org/abs/2307.08705)
* Zhang, Y. et al. (October 2023). [How well does LLM generate security tests?](https://arxiv.org/abs/2310.00710)
* Jing, D. (2022). [Improvement of Vulnerable Code Dataset Based on Program Equivalence Transformation](https://iopscience.iop.org/article/10.1088/1742-6596/2363/1/012010)
* Wu, Y. et al. (May 2023). [How Effective Are Neural Networks for Fixing Security Vulnerabilities](https://arxiv.org/abs/2305.18607)
* Yang, G. et al. (August 2021). [Few-Sample Named Entity Recognition for Security Vulnerability Reports by Fine-Tuning Pre-Trained Language Models](https://arxiv.org/abs/2108.06590)
* Zhou, J. et al. (2021). [Finding A Needle in a Haystack: Automated Mining of Silent Vulnerability Fixes](https://ieeexplore.ieee.org/abstract/document/9678720)
* Dunlap, T. et al. (2023). [Finding Fixed Vulnerabilities with Off-the-Shelf Static Analysis](https://ieeexplore.ieee.org/document/10190493)
* Shestov, A. et al. (January 2024). [Finetuning Large Language Models for Vulnerability Detection](https://arxiv.org/abs/2401.17010)
* Scalco, S. et al. (July 2024). [Hash4Patch: A Lightweight Low False Positive Tool for Finding Vulnerability Patch Commits](https://dl.acm.org/doi/10.1145/3643991.3644871)
* Nguyen-Truong, G. et al. (July 2022). [HERMES: Using Commit-Issue Linking to Detect Vulnerability-Fixing Commits](https://ieeexplore.ieee.org/abstract/document/9825835)
* Wang, J. et al. (July 2024). [Is Your AI-Generated Code Really Safe? Evaluating Large Language Models on Secure Code Generation with CodeSecEval](https://arxiv.org/abs/2407.02395)
* Sawadogo, A.D. et al. (January 2020). [Learning to Catch Security Patches](https://arxiv.org/abs/2001.09148)
* Tony, C. et al. (March 2023). [LLMSecEval: A Dataset of Natural Language Prompts for Security Evaluations](https://arxiv.org/abs/2303.09384)
* Wang, S., & Naggapan, N. (July 2019). [Characterizing and Understanding Software Developer Networks in Security Development](https://www.researchgate.net/publication/334760102_Characterizing_and_Understanding_Software_Developer_Networks_in_Security_Development)
* Chen, Z. et al. (April 2021). [Neural Transfer Learning for Repairing Security Vulnerabilities in C Code](https://arxiv.org/abs/2104.08308)
* Papotti, A. et al. (September 2022). [On the acceptance by code reviewers of candidate security patches suggested by Automated Program Repair tools](https://arxiv.org/abs/2209.07211)
* Mir, A.M. et al. (February 2024). [On the Effectiveness of Machine Learning-based Call Graph Pruning: An Empirical Study](https://arxiv.org/abs/2402.07294)
* Dietrich, J. et al. (June 2023). [On the Security Blind Spots of Software Composition Analysis](https://arxiv.org/abs/2306.05534)
* Triet H. M. Le., & Babar, A.M. (March 2022). [On the Use of Fine-grained Vulnerable Code Statements for Software Vulnerability Assessment Models](https://arxiv.org/abs/2203.08417)
* Chapman, J., & Venugopalan, H. (January 2023). [Open Source Software Computed Risk Framework](https://ieeexplore.ieee.org/abstract/document/10000561)
* Canfora, G. et al. (February 2022). [Patchworking: Exploring the code changes induced by vulnerability fixing activities](https://www.researchgate.net/publication/355561561_Patchworking_Exploring_the_code_changes_induced_by_vulnerability_fixing_activities)
* Garg, S. et al. (June 2021). [PerfLens: a data-driven performance bug detection and fix platform](https://dl.acm.org/doi/abs/10.1145/3460946.3464318)
* Coskun, T. et al. (November 2022). [Profiling developers to predict vulnerable code changes](https://dl.acm.org/doi/abs/10.1145/3558489.3559069)
* Bhuiyan, M.H.M. et al. (July 2023). [SecBench.js: An Executable Security Benchmark Suite for Server-Side JavaScript](https://ieeexplore.ieee.org/abstract/document/10172577)
* Reis, S. et al. (October 2022). [SECOM: towards a convention for security commit messages](https://dl.acm.org/doi/abs/10.1145/3524842.3528513)
* Bennett, G. et al. (June 2024). [Semgrep*: Improving the Limited Performance of Static Application Security Testing (SAST) Tools](https://dl.acm.org/doi/abs/10.1145/3661167.3661262)
* Chi, J. et al. (October 2020). [SeqTrans: Automatic Vulnerability Fix via Sequence to Sequence Learning](https://arxiv.org/abs/2010.10805)
* Ahmed, A. et al. (May 2023). [Sequential Graph Neural Networks for Source Code Vulnerability Identification](https://arxiv.org/abs/2306.05375)
* Sun, J. et al. (February 2023). [Silent Vulnerable Dependency Alert Prediction with Vulnerability Key Aspect Explanation](https://arxiv.org/abs/2302.07445)
* Zhao, L. et al. (November 2023). [Software Composition Analysis for Vulnerability Detection: An Empirical Study on Java Projects](https://dl.acm.org/doi/10.1145/3611643.3616299)
* Zhan, Q. et al. (January 2024). [Survey on Vulnerability Awareness of Open Source Software](https://www.jos.org.cn/josen/article/abstract/6935)
* Li, X. et al. (March 2023). [The anatomy of a vulnerability database: A systematic mapping study](https://www.sciencedirect.com/science/article/pii/S0164121223000742)
* Al Debeyan, F. et al. (February 2024). [The impact of hard and easy negative training data on vulnerability prediction performance☆](https://www.sciencedirect.com/science/article/pii/S0164121224000463)
* Xu, C. et al. (December 2021). [Tracking Patches for Open Source Software Vulnerabilities](https://arxiv.org/abs/2112.02240)
* Risse, N., & Böhme, M. (June 2023). [Uncovering the Limits of Machine Learning for Automatic Vulnerability Detection](https://arxiv.org/abs/2306.17193)
* Xu, N. et al. (July 2023). [Understanding and Tackling Label Errors in Deep Learning-Based Vulnerability Detection (Experience Paper)](https://dl.acm.org/doi/abs/10.1145/3597926.3598037)
* Wu, Y. et al. (July 2023). [Understanding the Threats of Upstream Vulnerabilities to Downstream Projects in the Maven Ecosystem](https://ieeexplore.ieee.org/abstract/document/10172868)
* Esposito, M., & Falessi, D. (March 2024). [VALIDATE: A deep dive into vulnerability prediction datasets](https://www.sciencedirect.com/science/article/pii/S0950584924000533)
* Wang, S. et al. (July 2022). [VCMatch: A Ranking-based Approach for Automatic Security Patches Localization for OSS Vulnerabilities](https://ieeexplore.ieee.org/abstract/document/9825908)
* Sun, Q. et al. (December 2022). [VERJava: Vulnerable Version Identification for Java OSS with a Two-Stage Analysis](https://ieeexplore.ieee.org/abstract/document/9978189)
* Nguyen, S. et al. (September 2023). [VFFINDER: A Graph-based Approach for Automated Silent Vulnerability-Fix Identification](https://arxiv.org/abs/2309.01971)
* Piran, A. et al. (March 2022). [Vulnerability Analysis of Similar Code](https://ieeexplore.ieee.org/abstract/document/9724745)
* Keller, P. et al. (February 2020). [What You See is What it Means! Semantic Representation Learning of Code based on Visualization and Transfer Learning](https://arxiv.org/abs/2002.02650)

___

**Our related papers**
* Cabrera Lozoya, R. et al. (March 2021). [Commit2Vec: Learning Distributed Representations of Code Changes](https://link.springer.com/article/10.1007/s42979-021-00566-z)
* Fehrer, T. et al. (May 2021). [Detecting Security Fixes in Open-Source Repositories using Static Code Analyzers](https://dl.acm.org/doi/pdf/10.1145/3661167.3661217)
* Ponta, S.E. et al. (June 2020). [Detection, assessment and mitigation of vulnerabilities in open source dependencies](https://www.semanticscholar.org/paper/Detection%2C-assessment-and-mitigation-of-in-open-Ponta-Plate/728eab7ac5ae7dd624d306ae5e1887f7b10447cc)
* Dann, A. et al. (September 2022). [Identifying Challenges for OSS Vulnerability Scanners - A Study & Test Suite](https://www.computer.org/csdl/journal/ts/2022/09/09506931/1vNfNyyKDOo)
* Ponta, S.E. et al. (August 2021). [The Used, the Bloated, and the Vulnerable: Reducing the Attack Surface of an Industrial Application](https://arxiv.org/abs/2108.05115)
* Iannone, E. et al. (June 2021). [Toward Automated Exploit Generation for Known Vulnerabilities in Open-Source Libraries](https://ieeexplore.ieee.org/abstract/document/9462983)

  
## Star History <a name="starhist"></a>

[![Star History Chart](https://api.star-history.com/svg?repos=sap/project-kb&type=Date)](https://star-history.com/#sap/project-kb&Date)

## Credits <a name="credit"></a>

### EU-funded research projects <a name="eu_funded"></a>

The development of Project KB is partially supported by the following projects:

* [Sec4AI4Sec](https://www.sec4ai4sec-project.eu/) (Grant No. 101120393)
* [AssureMOSS](https://assuremoss.eu) (Grant No. 952647).
* [Sparta](https://www.sparta.eu/) (Grant No. 830892).

### Vulnerability data sources <a name="vul_data"></a>

Vulnerability information from NVD and MITRE might have been used as input
for building parts of this knowledge base. See MITRE's [CVE Usage license](http://cve.mitre.org/about/termsofuse.html) for more information.

## Limitations and Known Issues <a name="limit"></a>

This project is **work-in-progress**, you can find the list of known issues [here](https://github.com/SAP/project-kb/issues). 

Currently the vulnerability knowledge base only contains information about vulnerabilities in Java and Python open source components.

## Support <a name="support"></a>

For the time being, please use [GitHub
issues](https://github.com/SAP/project-kb/issues) to report bugs, request new features and ask for support. 

## Contributing  <a name="contrib"></a>

See [How to contribute](CONTRIBUTING.md).
