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
1. [Kaybee](#kaybee)
2. [Prospector](#prosp)
3. [Vulnerability data](#vuldata)
4. [Publications](#publi)
5. [Star history](#starhist)
6. [Limitations and known issues](#limit)
7. [Support](#support)
8. [Contributing](#contrib)

## Description 

The goal of `Project KB` is to enable the creation, management and aggregation of a
distributed, collaborative knowledge base of vulnerabilities affecting
open-source software.

`Project KB` consists of vulnerability data [vulnerability knowledge-base](vulnerability-data)
as well as set of tools to support the mining, curation and management of such data.


### Motivations 

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

**Our papers related to Project KB**
* Sabetta, A., Ponta, S. E., Cabrera Lozoya, R., Bezzi, M., Sacchetti, T., Greco, M., … Massacci, F. (2024). [Known Vulnerabilities of Open Source Projects: Where Are the Fixes?](https://ieeexplore.ieee.org/document/10381645) IEEE Security & Privacy, 22(2), 49–59.
* Fehrer, T., Lozoya, R. C., Sabetta, A., Nucci, D. D., & Tamburri, D. A. (2024). [Detecting Security Fixes in Open-Source Repositories using Static Code Analyzers.](http://arxiv.org/abs/2105.03346) EASE '24: Proceedings of the 28th International Conference on Evaluation and Assessment in Software Engineering
* Dann, A., Plate, H., Hermann, B., Ponta, S., & Bodden, E. (2022). [Identifying Challenges for OSS Vulnerability Scanners - A Study & Test Suite.](https://ris.uni-paderborn.de/record/31132) IEEE Transactions on Software Engineering, 48(09), 3613–3625. 
* Cabrera Lozoya, R., Baumann, A., Sabetta, A., & Bezzi, M. (2021). [Commit2Vec: Learning Distributed Representations of Code Changes.](https://link.springer.com/article/10.1007/s42979-021-00566-z) SN Computer Science, 2(3).
* Ponta, S. E., Fischer, W., Plate, H., & Sabetta, A. (2021). [The Used, the Bloated, and the Vulnerable: Reducing the Attack Surface of an Industrial Application.](https://www.computer.org/csdl/proceedings-article/icsme/2021/288200a555/1yNhfKb2TBe) 2021 IEEE International Conference on Software Maintenance and Evolution (ICSME)
* Iannone, E., Nucci, D. D., Sabetta, A., & De Lucia, A. (2021). [Toward Automated Exploit Generation for Known Vulnerabilities in Open-Source Libraries.](https://ieeexplore.ieee.org/document/9462983) 2021 IEEE/ACM 29th International Conference on Program Comprehension (ICPC), 396–400.
* Ponta, S. E., Plate, H., & Sabetta, A. (2020). [Detection, assessment and mitigation of vulnerabilities in open source dependencies.](https://api.semanticscholar.org/CorpusID:220259876) Empirical Software Engineering, 25, 3175–3215. 

___

<!-- format used : APA -->

**Papers citing our work**
* Aladics, T., Hegedüs, P., & Ferenc, R. (2022). [A Vulnerability Introducing Commit Dataset for Java: An Improved SZZ based Approach.](https://api.semanticscholar.org/CorpusID:250566828) International Conference on Software and Data Technologies
* Bui, Q.-C., Scandariato, R., & Ferreyra, N. E. D. (2022). [Vul4J: a dataset of reproducible Java vulnerabilities geared towards the study of program repair techniques.](https://dl.acm.org/doi/abs/10.1145/3524842.3528482) Proceedings of the 19th International Conference on Mining Software Repositories, 464–468.
* S. R. Tate, M. Bollinadi, and J. Moore. (2020). [Characterizing Vulnerabilities in a Major Linux Distribution](https://home.uncg.edu/cmp/faculty/srtate/pubs/vulnerabilities/Vulnerabilities-SEKE2020.pdf) 32nd International Conference on Software Engineering \& Knowledge Engineering (SEKE), pp. 538-543.
* Galvão, P. (2022). [Analysis and Aggregation of Vulnerability Databases with Code-Level Data. Dissertation de Master's Degree.](https://repositorio-aberto.up.pt/bitstream/10216/144796/2/588886.pdf) Faculdade de Engenharia da Universidade do Porto.
* Sharma, T., Kechagia, M., Georgiou, S., Tiwari, R., Vats, I., Moazen, H., & Sarro, F. (2022). [A Survey on Machine Learning Techniques for Source Code Analysis.](http://arxiv.org/abs/2110.09610)
* Hommersom, D., Sabetta, A., Coppola, B., Nucci, D. D., & Tamburri, D. A. (2024). [Automated Mapping of Vulnerability Advisories onto their Fix Commits in Open Source Repositories.](https://dl.acm.org/doi/10.1145/3649590) ACM Trans. Softw. Eng. Methodol., 33(5).
* Marchand-Melsom, A., & Nguyen Mai, D. B. (2020). [Automatic repair of OWASP Top 10 security vulnerabilities: A survey.](https://dl.acm.org/doi/10.1145/3387940.3392200) Proceedings of the IEEE/ACM 42nd International Conference on Software Engineering Workshops, 23–30. Presented at the Seoul, Republic of Korea. 
* Sawadogo, A. D., Guimard, Q., Bissyandé, T. F., Kaboré, A. K., Klein, J., & Moha, N. (2021). [Early Detection of Security-Relevant Bug Reports using Machine Learning: How Far Are We?](http://arxiv.org/abs/2112.10123)
* Sun, S., Wang, S., Wang, X., Xing, Y., Zhang, E., & Sun, K. (2023). [Exploring Security Commits in Python.](http://arxiv.org/abs/2307.11853)
* Reis, S., Abreu, R., & Cruz, L. (2021). [Fixing Vulnerabilities Potentially Hinders Maintainability.](http://arxiv.org/abs/2106.03271)
* Andrade, R., & Santos, V. (2021). [Investigating vulnerability datasets.](https://sol.sbc.org.br/index.php/vem/article/view/17213) Anais Do IX Workshop de Visualização, Evolução e Manutenção de Software, 26–30. Presented at the Joinville. 
* Nguyen, T. G., Le-Cong, T., Kang, H. J., Widyasari, R., Yang, C., Zhao, Z., … Lo, D. (2023). [Multi-Granularity Detector for Vulnerability Fixes.](https://arxiv.org/abs/2305.13884) 
* Siddiq, M. L., & Santos, J. C. S. (2022). [SecurityEval dataset: mining vulnerability examples to evaluate machine learning-based code generation techniques.](https://dl.acm.org/doi/abs/10.1145/3549035.3561184) Proceedings of the 1st International Workshop on Mining Software Repositories Applications for Privacy and Security, 29–33. Presented at the Singapore, Singapore.]
* Sawadogo, A. D., Bissyandé, T. F., Moha, N., Allix, K., Klein, J., Li, L., & Traon, Y. L. (2020). [Learning to Catch Security Patches.](https://arxiv.org/abs/2001.09148)
* Dunlap, T., Lin, E., Enck, W., & Reaves, B. (2023). [VFCFinder: Seamlessly Pairing Security Advisories and Patches.](http://arxiv.org/abs/2311.01532)
* Bao, L., Xia, X., Hassan, A. E., & Yang, X. (2022). [V-SZZ: automatic identification of version ranges affected by CVE vulnerabilities.](https://dl.acm.org/doi/10.1145/3510003.3510113) Proceedings of the 44th International Conference on Software Engineering, 2352–2364. Presented at the Pittsburgh, Pennsylvania.
* Fan, J., Li, Y., Wang, S., & Nguyen, T. N. (2020). [A C/C++ Code Vulnerability Dataset with Code Changes and CVE Summaries.](https://dl.acm.org/doi/10.1145/3379597.3387501) Proceedings of the 17th International Conference on Mining Software Repositories, 508–512. Presented at the Seoul, Republic of Korea. 
* Zhang, Q., Fang, C., Ma, Y., Sun, W., & Chen, Z. (2023). [A Survey of Learning-based Automated Program Repair.](http://arxiv.org/abs/2301.03270)
* Alzubaidi, L., Bai, J., Al-Sabaawi, A., Santamaría, J. I., Albahri, A. S., Al-dabbagh, B. S. N., … Gu, Y. (2023). [A survey on deep learning tools dealing with data scarcity: definitions, challenges, solutions, tips, and applications.](https://www.semanticscholar.org/paper/A-survey-on-deep-learning-tools-dealing-with-data-Alzubaidi-Bai/4a07ded5f56aa76c75e844f353e046414b427cc2) Journal of Big Data, 10, 1–82. 
* Sharma, T., Kechagia, M., Georgiou, S., Tiwari, R., Vats, I., Moazen, H., & Sarro, F. (2024). [A survey on machine learning techniques applied to source code.](https://discovery.ucl.ac.uk/id/eprint/10184342/) Journal of Systems and Software, 209, 111934. 
* Elder, S., Rahman, M. R., Fringer, G., Kapoor, K., & Williams, L. (2024). [A Survey on Software Vulnerability Exploitability Assessment.](https://dl.acm.org/doi/10.1145/3648610) ACM Comput. Surv., 56(8). 
* Aladics, T., Hegedűs, P., & Ferenc, R. (2023). [An AST-based Code Change Representation and its Performance in Just-in-time Vulnerability Prediction.](https://arxiv.org/abs/2303.16591)
* Singhal, A., & Goel, P. K. (2023). [Analysis and Identification of Malicious Mobile Applications.](https://www.researchgate.net/publication/378257226_Analysis_and_Identification_of_Malicious_Mobile_Applications) 2023 3rd International Conference on Advancement in Electronics & Communication Engineering (AECE), 1045–1050. 
* Senanayake, J., Kalutarage, H., & Al-Kadri, M. O. (2021). [Android Mobile Malware Detection Using Machine Learning: A Systematic Review.](https://www.mdpi.com/2079-9292/10/13/1606) Electronics, 10(13). 
* Bui, Q.-C., Paramitha, R., Vu, D.-L., Massacci, F., & Scandariato, R. (12 2023). [APR4Vul: an empirical study of automatic program repair techniques on real-world Java vulnerabilities.](https://link.springer.com/article/10.1007/s10664-023-10415-7) Empirical Software Engineering, 29. 
* Senanayake, J., Kalutarage, H., Al-Kadri, M. O., Petrovski, A., & Piras, L. (2023). [Android Source Code Vulnerability Detection: A Systematic Literature Review.](https://dl.acm.org/doi/10.1145/3556974) ACM Comput. Surv., 55(9). 
* Reis, S., Abreu, R., & Pasareanu, C. (2023). [Are security commit messages informative? Not enough!](https://dl.acm.org/doi/10.1145/3593434.3593481) Proceedings of the 27th International Conference on Evaluation and Assessment in Software Engineering, 196–199. Presented at the Oulu, Finland. 
* [B EYOND SYNTAX TREES : LEARNING EMBEDDINGS OF CODE EDITS BY COMBINING MULTIPLE SOURCE REP - RESENTATIONS.](https://api.semanticscholar.org/CorpusID:249038879) (2022).
* Challande, A., David, R., & Renault, G. (2022). [Building a Commit-level Dataset of Real-world Vulnerabilities.](https://dl.acm.org/doi/10.1145/3508398.3511495) Proceedings of the Twelfth ACM Conference on Data and Application Security and Privacy, 101–106. Presented at the Baltimore, MD, USA. 
* Wang, Song, & Nagappan, N. (2019). [Characterizing and Understanding Software Developer Networks in Security Development.](http://arxiv.org/abs/1907.12141) 
* Harzevili, N. S., Shin, J., Wang, J., & Wang, S. (2022). [Characterizing and Understanding Software Security Vulnerabilities in Machine Learning Libraries.](http://arxiv.org/abs/2203.06502)
* Zhang, L., Liu, C., Xu, Z., Chen, S., Fan, L., Zhao, L., … Liu, Y. (2023). [Compatible Remediation on Vulnerabilities from Third-Party Libraries for Java Projects.](http://arxiv.org/abs/2301.08434)
* Lee, J. Y. D., & Chieu, H. L. (2021, November). [Co-training for Commit Classification.](https://aclanthology.org/2021.wnut-1.43/)
* In W. Xu, A. Ritter, T. Baldwin, & A. Rahimi (Eds.), [Proceedings of the Seventh Workshop on Noisy User-generated Text (W-NUT 2021)](https://aclanthology.org/volumes/2021.wnut-1/)
* Nikitopoulos, G., Dritsa, K., Louridas, P., & Mitropoulos, D. (2021).[CrossVul: a cross-language vulnerability dataset with commit data.](https://dl.acm.org/doi/10.1145/3468264.3473122) Proceedings of the 29th ACM Joint Meeting on European Software Engineering Conference and Symposium on the Foundations of Software Engineering, 1565–1569. Presented at the Athens, Greece. 
* Bhandari, G., Naseer, A., & Moonen, L. (2021, August). [CVEfixes: automated collection of vulnerabilities and their fixes from open-source software.](https://arxiv.org/abs/2107.08760) Proceedings of the 17th International Conference on Predictive Models and Data Analytics in Software Engineering. 
* Sonnekalb, T., Heinze, T. S., & Mäder, P. (2022). [Deep security analysis of program code: A systematic literature review.](https://link.springer.com/article/10.1007/s10664-021-10029-x) Empirical Softw. Engg., 27(1).
* Le, T. H. M., Hin, D., Croft, R., & Babar, M. A. (2021). [DeepCVA: Automated Commit-level Vulnerability Assessment with Deep Multi-task Learning.](http://arxiv.org/abs/2108.08041)
* Senanayake, J., Kalutarage, H., Petrovski, A., Piras, L., & Al-Kadri, M. O. (2024). [Defendroid: Real-time Android code vulnerability detection via blockchain federated neural network with XAI.](https://www.sciencedirect.com/science/article/pii/S2214212624000449) Journal of Information Security and Applications, 82, 103741. 
* Stefanoni, A., Girdzijauskas, S., Jenkins, C., Kefato, Z. T., Sbattella, L., Scotti, V., & Wåreus, E. (2022). [Detecting Security Patches in Java Projects Using NLP Technology.](https://api.semanticscholar.org/CorpusID:256739262) International Conference on Natural Language and Speech Processing. 
* Okutan, A., Mell, P., Mirakhorli, M., Khokhlov, I., Santos, J. C. S., Gonzalez, D., & Simmons, S. (2023). [Empirical Validation of Automated Vulnerability Curation and Characterization.](https://ieeexplore.ieee.org/document/10056768) IEEE Transactions on Software Engineering, 49(5), 3241–3260. 
* Wang, J., Cao, L., Luo, X., Zhou, Z., Xie, J., Jatowt, A., & Cai, Y. (2023). [Enhancing Large Language Models for Secure Code Generation: A Dataset-driven Study on Vulnerability Mitigation.](http://arxiv.org/abs/2310.16263)
* Bottner, L., Hermann, A., Eppler, J., Thüm, T., & Kargl, F. (2023). [Evaluation of Free and Open Source Tools for Automated Software Composition Analysis.](https://dl.acm.org/doi/abs/10.1145/3631204.3631862) Proceedings of the 7th ACM Computer Science in Cars Symposium. Presented at the Darmstadt, Germany.
* Ganz, T., Härterich, M., Warnecke, A., & Rieck, K. (2021). [Explaining Graph Neural Networks for Vulnerability Discovery.](doi:10.1145/3474369.3486866) Proceedings of the 14th ACM Workshop on Artificial Intelligence and Security, 145–156. Presented at the Virtual Event, Republic of Korea. 
* Ram, A., Xin, J., Nagappan, M., Yu, Y., Lozoya, R. C., Sabetta, A., & Lin, J. (2019). [Exploiting Token and Path-based Representations of Code for Identifying Security-Relevant Commits.](http://arxiv.org/abs/1911.07620)
* Rahman, M. M., Watanobe, Y., Shirafuji, A., & Hamada, M. (2023). [Exploring Automated Code Evaluation Systems and Resources for Code Analysis: A Comprehensive Survey.](http://arxiv.org/abs/2307.08705)
* Zhang, Y., Song, W., Ji, Z., Danfeng, Yao, & Meng, N. (2023). [How well does LLM generate security tests?](http://arxiv.org/abs/2310.00710)
* Jing, D. (2022). [Improvement of Vulnerable Code Dataset Based on Program Equivalence Transformation.](https://iopscience.iop.org/article/10.1088/1742-6596/2363/1/012010/pdf) Journal of Physics: Conference Series, 2363(1), 012010. 
* Wu, Yi, Jiang, N., Pham, H. V., Lutellier, T., Davis, J., Tan, L., … Shah, S. (2023, July). [How Effective Are Neural Networks for Fixing Security Vulnerabilities.](https://arxiv.org/abs/2305.18607) Proceedings of the 32nd ACM SIGSOFT International Symposium on Software Testing and Analysis. 
* Yang, G., Dineen, S., Lin, Z., & Liu, X. (2021). [Few-Sample Named Entity Recognition for Security Vulnerability Reports by Fine-Tuning Pre-Trained Language Models.](http://arxiv.org/abs/2108.06590)
* Zhou, J., Pacheco, M., Wan, Z., Xia, X., Lo, D., Wang, Y., & Hassan, A. E. (2021). [Finding A Needle in a Haystack: Automated Mining of Silent Vulnerability Fixes.](https://ieeexplore.ieee.org/document/9678720) 2021 36th IEEE/ACM International Conference on Automated Software Engineering (ASE), 705–716. 
* Dunlap, T., Thorn, S., Enck, W., & Reaves, B. (2023). [Finding Fixed Vulnerabilities with Off-the-Shelf Static Analysis.](https://ieeexplore.ieee.org/document/10190493) 2023 IEEE 8th European Symposium on Security and Privacy (EuroS&P), 489–505. 
* Shestov, A., Levichev, R., Mussabayev, R., Maslov, E., Cheshkov, A., & Zadorozhny, P. (2024). [Finetuning Large Language Models for Vulnerability Detection.](http://arxiv.org/abs/2401.17010)
* Scalco, S., & Paramitha, R. (2024). [Hash4Patch: A Lightweight Low False Positive Tool for Finding Vulnerability Patch Commits.](https://dl.acm.org/doi/10.1145/3643991.3644871) Proceedings of the 21st International Conference on Mining Software Repositories, 733–737. Presented at the Lisbon, Portugal. 
* Nguyen-Truong, G., Kang, H. J., Lo, D., Sharma, A., Santosa, A. E., Sharma, A., & Ang, M. Y. (2022). [HERMES: Using Commit-Issue Linking to Detect Vulnerability-Fixing Commits.](https://ieeexplore.ieee.org/document/9825835) 2022 IEEE International Conference on Software Analysis, Evolution and Reengineering (SANER), 51–62. 
* Wang, J., Luo, X., Cao, L., He, H., Huang, H., Xie, J., … Cai, Y. (2024). [Is Your AI-Generated Code Really Safe? Evaluating Large Language Models on Secure Code Generation with CodeSecEval.](http://arxiv.org/abs/2407.02395)
* Tony, C., Mutas, M., Ferreyra, N. E. D., & Scandariato, R. (2023). [LLMSecEval: A Dataset of Natural Language Prompts for Security Evaluations.](http://arxiv.org/abs/2303.09384)
* Chen, Z., Kommrusch, S., & Monperrus, M. (2023). [Neural Transfer Learning for Repairing Security Vulnerabilities in C Code.](https://ieeexplore.ieee.org/document/9699412) IEEE Transactions on Software Engineering, 49(1), 147–165. 
* Papotti, A., Paramitha, R., & Massacci, F. (2022). [On the acceptance by code reviewers of candidate security patches suggested by Automated Program Repair tools.](http://arxiv.org/abs/2209.07211)
* Mir, A. M., Keshani, M., & Proksch, S. (2024). [On the Effectiveness of Machine Learning-based Call Graph Pruning: An Empirical Study.](http://arxiv.org/abs/2402.07294)
* Dietrich, J., Rasheed, S., Jordan, A., & White, T. (2023). [On the Security Blind Spots of Software Composition Analysis.](http://arxiv.org/abs/2306.05534)
* Le, T. H. M., & Babar, M. A. (2022). [On the Use of Fine-grained Vulnerable Code Statements for Software Vulnerability Assessment Models.](http://arxiv.org/abs/2203.08417)
* Chapman, J., & Venugopalan, H. (2022). [Open Source Software Computed Risk Framework.](https://www.bibsonomy.org/bibtex/1c114d6756c609391db2f66919f237261) 2022 IEEE 17th International Conference on Computer Sciences and Information Technologies (CSIT), 172–175. 
* Canfora, G., Di Sorbo, A., Forootani, S., Martinez, M., & Visaggio, C. A. (2022). [Patchworking: Exploring the code changes induced by vulnerability fixing activities.](https://www.sciencedirect.com/science/article/abs/pii/S0950584921001932) Information and Software Technology, 142, 106745. 
* Garg, S., Moghaddam, R. Z., Sundaresan, N., & Wu, C. (2021). [PerfLens: a data-driven performance bug detection and fix platform.](https://dl.acm.org/doi/10.1145/3460946.3464318) Proceedings of the 10th ACM SIGPLAN International Workshop on the State Of the Art in Program Analysis, 19–24. Presented at the Virtual, Canada. 
* Coskun, T., Halepmollasi, R., Hanifi, K., Fouladi, R. F., De Cnudde, P. C., & Tosun, A. (2022). [Profiling developers to predict vulnerable code changes.](https://dl.acm.org/doi/10.1145/3558489.3559069) Proceedings of the 18th International Conference on Predictive Models and Data Analytics in Software Engineering, 32–41. Presented at the Singapore, Singapore. 
* Bhuiyan, M. H. M., Parthasarathy, A. S., Vasilakis, N., Pradel, M., & Staicu, C.-A. (2023). [SecBench.js: An Executable Security Benchmark Suite for Server-Side JavaScript.](https://ieeexplore.ieee.org/document/10172577) 2023 IEEE/ACM 45th International Conference on Software Engineering (ICSE), 1059–1070. 
* Reis, S., Abreu, R., Erdogmus, H., & Păsăreanu, C. (2022). [SECOM: towards a convention for security commit messages.](https://dl.acm.org/doi/abs/10.1145/3524842.3528513) Proceedings of the 19th International Conference on Mining Software Repositories, 764–765. Presented at the Pittsburgh, Pennsylvania. 
* Bennett, G., Hall, T., Winter, E., & Counsell, S. (2024). [Semgrep*: Improving the Limited Performance of Static Application Security Testing (SAST) Tools.](https://dl.acm.org/doi/10.1145/3661167.3661262) Proceedings of the 28th International Conference on Evaluation and Assessment in Software Engineering, 614–623. Salerno, Italy. 
* Chi, J., Qu, Y., Liu, T., Zheng, Q., & Yin, H. (2022). [SeqTrans: Automatic Vulnerability Fix via Sequence to Sequence Learning.](http://arxiv.org/abs/2010.10805)
* Ahmed, A., Said, A., Shabbir, M., & Koutsoukos, X. (2023). [Sequential Graph Neural Networks for Source Code Vulnerability Identification.](http://arxiv.org/abs/2306.05375)
* Sun, J., Xing, Z., Lu, Q., Xu, X., Zhu, L., Hoang, T., & Zhao, D. (2023). [Silent Vulnerable Dependency Alert Prediction with Vulnerability Key Aspect Explanation.](http://arxiv.org/abs/2302.07445)
* Zhao, L., Chen, S., Xu, Z., Liu, C., Zhang, L., Wu, J., … Liu, Y. (2023). [Software Composition Analysis for Vulnerability Detection: An Empirical Study on Java Projects.](https://dl.acm.org/doi/10.1145/3611643.3616299) Proceedings of the 31st ACM Joint European Software Engineering Conference and * Symposium on the Foundations of Software Engineering, 960–972. Presented at the San Francisco, CA, USA. 
* ZHAN, Q., PAN S-Y., HU X., BAO L-F., XIA, X. (2024). [Survey on Vulnerability Awareness of Open Source Software.](https://www.jos.org.cn/josen/article/abstract/6935) Journal of Software, 35(1), 19. 
* Li, X., Moreschini, S., Zhang, Z., Palomba, F., & Taibi, D. (2023). [The anatomy of a vulnerability database: A systematic mapping study.](https://www.sciencedirect.com/science/article/pii/S0164121223000742) Journal of Systems and Software, 201, 111679. 
* Al Debeyan, F., Madeyski, L., Hall, T., & Bowes, D. (2024). [The impact of hard and easy negative training data on vulnerability prediction performance.](https://www.sciencedirect.com/science/article/pii/S0164121224000463) Journal of Systems and Software, 211, 112003. 
* Xu, C., Chen, B., Lu, C., Huang, K., Peng, X., & Liu, Y. (2023). [Tracking Patches for Open Source Software Vulnerabilities.](http://arxiv.org/abs/2112.02240)
* Risse, N., & Böhme, M. (2024). [Uncovering the Limits of Machine Learning for Automatic Vulnerability Detection.](http://arxiv.org/abs/2306.17193)
* Nie, X., Li, N., Wang, K., Wang, S., Luo, X., & Wang, H. (2023). [Understanding and Tackling Label Errors in Deep Learning-Based Vulnerability Detection (Experience Paper).](https://dl.acm.org/doi/10.1145/3597926.3598037) Proceedings of the 32nd ACM SIGSOFT International Symposium on Software Testing and Analysis, 52–63. Presented at the Seattle, WA, USA. 
* Wu, Yulun, Yu, Z., Wen, M., Li, Q., Zou, D., & Jin, H. (2023). [Understanding the Threats of Upstream Vulnerabilities to Downstream Projects in the Maven Ecosystem.](https://dl.acm.org/doi/10.1109/ICSE48619.2023.00095) 2023 IEEE/ACM 45th International Conference on Software Engineering (ICSE), 1046–1058. 
* Esposito, M., & Falessi, D. (2024). [VALIDATE: A deep dive into vulnerability prediction datasets.](https://dl.acm.org/doi/abs/10.1016/j.infsof.2024.107448) Information and Software Technology, 170, 107448. 
* Wang, Shichao, Zhang, Y., Bao, L., Xia, X., & Wu, M. (2022). [VCMatch: A Ranking-based Approach for Automatic Security Patches Localization for OSS Vulnerabilities.](https://ieeexplore.ieee.org/document/9825908) 2022 IEEE International Conference on Software Analysis, Evolution and Reengineering (SANER), 589–600. 
* Sun, Q., Xu, L., Xiao, Y., Li, F., Su, H., Liu, Y., … Huo, W. (2022). [VERJava: Vulnerable Version Identification for Java OSS with a Two-Stage Analysis.](https://ieeexplore.ieee.org/document/9978189) 2022 IEEE International Conference on Software Maintenance and Evolution (ICSME), 329–339. 
* Nguyen, S., Vu, T. T., & Vo, H. D. (2023). [VFFINDER: A Graph-based Approach for Automated Silent Vulnerability-Fix Identification.](http://arxiv.org/abs/2309.01971)
* Piran, A., Chang, C.-P., & Fard, A. M. (2021). [Vulnerability Analysis of Similar Code.](https://ieeexplore.ieee.org/document/9724745) 2021 IEEE 21st International Conference on Software Quality, Reliability and Security (QRS), 664–671. 
* Keller, P., Plein, L., Bissyandé, T. F., Klein, J., & Traon, Y. L. (2020). [What You See is What it Means! Semantic Representation Learning of Code based on Visualization and Transfer Learning.](http://arxiv.org/abs/2002.02650)
* Akhoundali, J., Nouri, S. R., Rietveld, K., & Gadyatskaya, O. (2024). [MoreFixes: A Large-Scale Dataset of CVE Fix Commits Mined through Enhanced Repository Discovery.](https://dl.acm.org/doi/10.1145/3663533.3664036) Proceedings of the 20th International Conference on Predictive Models and Data Analytics in Software Engineering, 42–51. Presented at the Porto de Galinhas, Brazil.

## Star History <a name="starhist"></a>

[![Star History Chart](https://api.star-history.com/svg?repos=sap/project-kb&type=Date)](https://star-history.com/#sap/project-kb&Date)

## Credits <a name="credit"></a>

### EU-funded research projects 

The development of Project KB is partially supported by the following projects:

* [Sec4AI4Sec](https://www.sec4ai4sec-project.eu/) (Grant No. 101120393)
* [AssureMOSS](https://assuremoss.eu) (Grant No. 952647).
* [Sparta](https://www.sparta.eu/) (Grant No. 830892).

### Vulnerability data sources 

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
