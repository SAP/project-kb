# Project KB

[![Go Report Card](https://goreportcard.com/badge/github.com/sap/project-kb)](https://goreportcard.com/report/github.com/sap/project-kb)
[![Go](https://github.com/sap/project-kb/workflows/Go/badge.svg)](https://github.com/SAP/project-kb/actions?query=workflow%3AGo)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/SAP/project-kb/blob/master/LICENSE.txt)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/sap/project-kb/#contributing)
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

### Our papers related to Project KB
* Sabetta, A., Ponta, S. E., Cabrera Lozoya, R., Bezzi, M., Sacchetti, T., Greco, M., … Massacci, F. (2024). [Known Vulnerabilities of Open Source Projects: Where Are the Fixes?](https://ieeexplore.ieee.org/document/10381645) IEEE Security & Privacy, 22(2), 49–59.
* Fehrer, T., Lozoya, R. C., Sabetta, A., Nucci, D. D., & Tamburri, D. A. (2024). [Detecting Security Fixes in Open-Source Repositories using Static Code Analyzers.](http://arxiv.org/abs/2105.03346) EASE '24: Proceedings of the 28th International Conference on Evaluation and Assessment in Software Engineering
* Dann, A., Plate, H., Hermann, B., Ponta, S., & Bodden, E. (2022). [Identifying Challenges for OSS Vulnerability Scanners - A Study & Test Suite.](https://ris.uni-paderborn.de/record/31132) IEEE Transactions on Software Engineering, 48(09), 3613–3625.
* Cabrera Lozoya, R., Baumann, A., Sabetta, A., & Bezzi, M. (2021). [Commit2Vec: Learning Distributed Representations of Code Changes.](https://link.springer.com/article/10.1007/s42979-021-00566-z) SN Computer Science, 2(3).
* Ponta, S. E., Fischer, W., Plate, H., & Sabetta, A. (2021). [The Used, the Bloated, and the Vulnerable: Reducing the Attack Surface of an Industrial Application.](https://www.computer.org/csdl/proceedings-article/icsme/2021/288200a555/1yNhfKb2TBe) 2021 IEEE International Conference on Software Maintenance and Evolution (ICSME)
* Iannone, E., Nucci, D. D., Sabetta, A., & De Lucia, A. (2021). [Toward Automated Exploit Generation for Known Vulnerabilities in Open-Source Libraries.](https://ieeexplore.ieee.org/document/9462983) 2021 IEEE/ACM 29th International Conference on Program Comprehension (ICPC), 396–400.
* Ponta, S. E., Plate, H., & Sabetta, A. (2020). [Detection, assessment and mitigation of vulnerabilities in open source dependencies.](https://api.semanticscholar.org/CorpusID:220259876) Empirical Software Engineering, 25, 3175–3215.
* Achyudh Ram, Ji Xin, Meiyappan Nagappan, Yaoliang Yu, Rocío Cabrera Lozoya, Antonino Sabetta, and Jimmy Lin. [Exploiting Token and Path-based Representations of Code for Identifying Security-Relevant Commits](https://arxiv.org/abs/1911.07620). arXiv. (2019).
___

<!-- format used : APA -->

### Papers citing our work

  * Tushar Sharma, Maria Kechagia, Stefanos Georgiou, Rohit Tiwari, Indira Vats, Hadi Moazen, and Federica Sarro. [A survey on machine learning techniques applied to source code](https://www.sciencedirect.com/science/article/pii/S0164121223003291). Journal of Systems and Software. (2024).

  * Elder, Sarah, Rahman, Md Rayhanur, Fringer, Gage, Kapoor, Kunal, and Williams, Laurie. [A Survey on Software Vulnerability Exploitability Assessment](https://doi.org/10.1145/3648610). ACM Comput. Surv.. (2024).

  * Janaka Senanayake, Harsha Kalutarage, Andrei Petrovski, Luca Piras, and Mhd Omar Al-Kadri. [Defendroid: Real-time Android code vulnerability detection via blockchain federated neural network with XAI](https://www.sciencedirect.com/science/article/pii/S2214212624000449). Journal of Information Security and Applications. (2024).

  * Alexey Shestov, Rodion Levichev, Ravil Mussabayev, Evgeny Maslov, Anton Cheshkov, and Pavel Zadorozhny. [Finetuning Large Language Models for Vulnerability Detection](https://arxiv.org/abs/2401.17010). arXiv. (2024).

  * Scalco, Simone, and Paramitha, Ranindya. [Hash4Patch: A Lightweight Low False Positive Tool for Finding Vulnerability Patch Commits](https://doi.org/10.1145/3643991.3644871). Proceedings of the 21st International Conference on Mining Software Repositories. (2024).

  * Jiexin Wang, Xitong Luo, Liuwen Cao, Hongkui He, Hailin Huang, Jiayuan Xie, Adam Jatowt, and Yi Cai. [Is Your AI-Generated Code Really Safe? Evaluating Large Language Models on Secure Code Generation with CodeSecEval](https://arxiv.org/abs/2407.02395). arXiv. (2024).

  * Amir M. Mir, Mehdi Keshani, and Sebastian Proksch. [On the Effectiveness of Machine Learning-based Call Graph Pruning: An Empirical Study](https://arxiv.org/abs/2402.07294). arXiv. (2024).

  * Bennett, Gareth, Hall, Tracy, Winter, Emily, and Counsell, Steve. [Semgrep*: Improving the Limited Performance of Static Application Security Testing (SAST) Tools](https://doi.org/10.1145/3661167.3661262). Proceedings of the 28th International Conference on Evaluation and Assessment in Software Engineering. (2024).

  * ZHAN Qi, PAN Sheng-Yi, HU Xing, BAO Ling-Feng, XIA Xin. Survey on Vulnerability Awareness of Open Source Software. Journal of Software. (2024).

  * Fahad {Al Debeyan}, Lech Madeyski, Tracy Hall, and David Bowes. [The impact of hard and easy negative training data on vulnerability prediction performance](https://www.sciencedirect.com/science/article/pii/S0164121224000463). Journal of Systems and Software. (2024).

  * Niklas Risse, and Marcel Böhme. [Uncovering the Limits of Machine Learning for Automatic Vulnerability Detection](https://arxiv.org/abs/2306.17193). arXiv. (2024).

  * Matteo Esposito, and Davide Falessi. [VALIDATE: A deep dive into vulnerability prediction datasets](https://www.sciencedirect.com/science/article/pii/S0950584924000533). Information and Software Technology. (2024).

  * Akhoundali, Jafar, Nouri, Sajad Rahim, Rietveld, Kristian, and Gadyatskaya, Olga. [MoreFixes: A Large-Scale Dataset of CVE Fix Commits Mined through Enhanced Repository Discovery](https://doi.org/10.1145/3663533.3664036). Proceedings of the 20th International Conference on Predictive Models and Data Analytics in Software Engineering. (2024).

  * Shiyu Sun, Shu Wang, Xinda Wang, Yunlong Xing, Elisa Zhang, and Kun Sun. [Exploring Security Commits in Python](https://arxiv.org/abs/2307.11853). arXiv. (2023).

  * Truong Giang Nguyen, Thanh Le-Cong, Hong Jin Kang, Ratnadira Widyasari, Chengran Yang, Zhipeng Zhao, Bowen Xu, Jiayuan Zhou, Xin Xia, Ahmed E. Hassan, Xuan-Bach D. Le, and David Lo. [Multi-Granularity Detector for Vulnerability Fixes](https://arxiv.org/abs/2305.13884). arXiv. (2023).

  * Trevor Dunlap, Elizabeth Lin, William Enck, and Bradley Reaves. [VFCFinder: Seamlessly Pairing Security Advisories and Patches](https://arxiv.org/abs/2311.01532). arXiv. (2023).

  * Quanjun Zhang, Chunrong Fang, Yuxiang Ma, Weisong Sun, and Zhenyu Chen. [A Survey of Learning-based Automated Program Repair](https://arxiv.org/abs/2301.03270). arXiv. (2023).

  * Laith Alzubaidi, Jinshuai Bai, Aiman Al-Sabaawi, Jos{\'e} I. Santamar{\'i}a, Ahmed Shihab Albahri, Bashar Sami Nayyef Al-dabbagh, Mohammed Abdulraheem Fadhel, Mohamed Manoufali, Jinglan Zhang, Ali H. Al-timemy, Ye Duan, Amjed Abdullah, Laith Farhan, Yi Lu, Ashish Gupta, Felix Albu, Amin Abbosh, and Yuantong Gu. [A survey on deep learning tools dealing with data scarcity: definitions, challenges, solutions, tips, and applications](https://api.semanticscholar.org/CorpusID:258137181). Journal of Big Data. (2023).

  * Tamás Aladics, Péter Hegedűs, and Rudolf Ferenc. [An AST-based Code Change Representation and its Performance in Just-in-time Vulnerability Prediction](https://arxiv.org/abs/2303.16591). arXiv. (2023).

  * Singhal, Amit, and Goel, Pawan Kumar. Analysis and Identification of Malicious Mobile Applications. 2023 3rd International Conference on Advancement in Electronics & Communication Engineering (AECE). (2023).

  * Bui, Quang-Cuong, Paramitha, Ranindya, Vu, Duc-Ly, Massacci, Fabio, and Scandariato, Riccardo. APR4Vul: an empirical study of automatic program repair techniques on real-world Java vulnerabilities. Empirical Software Engineering. (2023).

  * Senanayake, Janaka, Kalutarage, Harsha, Al-Kadri, Mhd Omar, Petrovski, Andrei, and Piras, Luca. [Android Source Code Vulnerability Detection: A Systematic Literature Review](https://doi.org/10.1145/3556974). ACM Comput. Surv.. (2023).

  * Reis, Sofia, Abreu, Rui, and Pasareanu, Corina. [Are security commit messages informative? Not enough!](https://doi.org/10.1145/3593434.3593481). Proceedings of the 27th International Conference on Evaluation and Assessment in Software Engineering. (2023).

  * Lyuye Zhang, Chengwei Liu, Zhengzi Xu, Sen Chen, Lingling Fan, Lida Zhao, Jiahui Wu, and Yang Liu. [Compatible Remediation on Vulnerabilities from Third-Party Libraries for Java Projects](https://arxiv.org/abs/2301.08434). arXiv. (2023).

  * Okutan, Ahmet, Mell, Peter, Mirakhorli, Mehdi, Khokhlov, Igor, Santos, Joanna C. S., Gonzalez, Danielle, and Simmons, Steven. Empirical Validation of Automated Vulnerability Curation and Characterization. IEEE Transactions on Software Engineering. (2023).

  * Jiexin Wang, Liuwen Cao, Xitong Luo, Zhiping Zhou, Jiayuan Xie, Adam Jatowt, and Yi Cai. [Enhancing Large Language Models for Secure Code Generation: A Dataset-driven Study on Vulnerability Mitigation](https://arxiv.org/abs/2310.16263). arXiv. (2023).

  * Bottner, Laura, Hermann, Artur, Eppler, Jeremias, Th\"{u}m, Thomas, and Kargl, Frank. [Evaluation of Free and Open Source Tools for Automated Software Composition Analysis](https://doi.org/10.1145/3631204.3631862). Proceedings of the 7th ACM Computer Science in Cars Symposium. (2023).

  * Md. Mostafizer Rahman, Yutaka Watanobe, Atsushi Shirafuji, and Mohamed Hamada. [Exploring Automated Code Evaluation Systems and Resources for Code Analysis: A Comprehensive Survey](https://arxiv.org/abs/2307.08705). arXiv. (2023).

  * Ying Zhang, Wenjia Song, Zhengjie Ji, Danfeng, Yao, and Na Meng. [How well does LLM generate security tests?](https://arxiv.org/abs/2310.00710). arXiv. (2023).

  * Wu, Yi, Jiang, Nan, Pham, Hung Viet, Lutellier, Thibaud, Davis, Jordan, Tan, Lin, Babkin, Petr, and Shah, Sameena. [How Effective Are Neural Networks for Fixing Security Vulnerabilities](http://dx.doi.org/10.1145/3597926.3598135). Proceedings of the 32nd ACM SIGSOFT International Symposium on Software Testing and Analysis. (2023).

  * Dunlap, Trevor, Thorn, Seaver, Enck, William, and Reaves, Bradley. Finding Fixed Vulnerabilities with Off-the-Shelf Static Analysis. 2023 IEEE 8th European Symposium on Security and Privacy (EuroS&P). (2023).

  * Catherine Tony, Markus Mutas, Nicolás E. Díaz Ferreyra, and Riccardo Scandariato. [LLMSecEval: A Dataset of Natural Language Prompts for Security Evaluations](https://arxiv.org/abs/2303.09384). arXiv. (2023).

  * Chen, Zimin, Kommrusch, Steve, and Monperrus, Martin. [Neural Transfer Learning for Repairing Security Vulnerabilities in C Code](http://dx.doi.org/10.1109/TSE.2022.3147265). IEEE Transactions on Software Engineering. (2023).

  * Jens Dietrich, Shawn Rasheed, Alexander Jordan, and Tim White. [On the Security Blind Spots of Software Composition Analysis](https://arxiv.org/abs/2306.05534). arXiv. (2023).

  * Bhuiyan, Masudul Hasan Masud, Parthasarathy, Adithya Srinivas, Vasilakis, Nikos, Pradel, Michael, and Staicu, Cristian-Alexandru. SecBench.js: An Executable Security Benchmark Suite for Server-Side JavaScript. 2023 IEEE/ACM 45th International Conference on Software Engineering (ICSE). (2023).

  * Ammar Ahmed, Anwar Said, Mudassir Shabbir, and Xenofon Koutsoukos. [Sequential Graph Neural Networks for Source Code Vulnerability Identification](https://arxiv.org/abs/2306.05375). arXiv. (2023).

  * Jiamou Sun, Zhenchang Xing, Qinghua Lu, Xiwei Xu, Liming Zhu, Thong Hoang, and Dehai Zhao. [Silent Vulnerable Dependency Alert Prediction with Vulnerability Key Aspect Explanation](https://arxiv.org/abs/2302.07445). arXiv. (2023).

  * Zhao, Lida, Chen, Sen, Xu, Zhengzi, Liu, Chengwei, Zhang, Lyuye, Wu, Jiahui, Sun, Jun, and Liu, Yang. [Software Composition Analysis for Vulnerability Detection: An Empirical Study on Java Projects](https://doi.org/10.1145/3611643.3616299). Proceedings of the 31st ACM Joint European Software Engineering Conference and Symposium on the Foundations of Software Engineering. (2023).

  * Xiaozhou Li, Sergio Moreschini, Zheying Zhang, Fabio Palomba, and Davide Taibi. [The anatomy of a vulnerability database: A systematic mapping study](https://www.sciencedirect.com/science/article/pii/S0164121223000742). Journal of Systems and Software. (2023).

  * Congying Xu, Bihuan Chen, Chenhao Lu, Kaifeng Huang, Xin Peng, and Yang Liu. [Tracking Patches for Open Source Software Vulnerabilities](https://arxiv.org/abs/2112.02240). arXiv. (2023).

  * Nie, Xu, Li, Ningke, Wang, Kailong, Wang, Shangguang, Luo, Xiapu, and Wang, Haoyu. [Understanding and Tackling Label Errors in Deep Learning-Based Vulnerability Detection (Experience Paper)](https://doi.org/10.1145/3597926.3598037). Proceedings of the 32nd ACM SIGSOFT International Symposium on Software Testing and Analysis. (2023).

  * Wu, Yulun, Yu, Zeliang, Wen, Ming, Li, Qiang, Zou, Deqing, and Jin, Hai. Understanding the Threats of Upstream Vulnerabilities to Downstream Projects in the Maven Ecosystem. 2023 IEEE/ACM 45th International Conference on Software Engineering (ICSE). (2023).

  * Son Nguyen, Thanh Trong Vu, and Hieu Dinh Vo. [VFFINDER: A Graph-based Approach for Automated Silent Vulnerability-Fix Identification](https://arxiv.org/abs/2309.01971). arXiv. (2023).

  * Tam{\'a}s Aladics, P{\'e}ter Heged{\"u}s, and Rudolf Ferenc. [A Vulnerability Introducing Commit Dataset for Java: An Improved SZZ based Approach](https://api.semanticscholar.org/CorpusID:250566828). International Conference on Software and Data Technologies. (2022).

  * Bui, Quang-Cuong, Scandariato, Riccardo, and Ferreyra, Nicol\'{a}s E. D\'{\i}az. [Vul4J: a dataset of reproducible Java vulnerabilities geared towards the study of program repair techniques](https://doi.org/10.1145/3524842.3528482). Proceedings of the 19th International Conference on Mining Software Repositories. (2022).

  * Tushar Sharma, Maria Kechagia, Stefanos Georgiou, Rohit Tiwari, Indira Vats, Hadi Moazen, and Federica Sarro. [A Survey on Machine Learning Techniques for Source Code Analysis](https://arxiv.org/abs/2110.09610). arXiv. (2022).

  * Siddiq, Mohammed Latif, and Santos, Joanna C. S.. [SecurityEval dataset: mining vulnerability examples to evaluate machine learning-based code generation techniques](https://doi.org/10.1145/3549035.3561184). Proceedings of the 1st International Workshop on Mining Software Repositories Applications for Privacy and Security. (2022).

  * Bao, Lingfeng, Xia, Xin, Hassan, Ahmed E., and Yang, Xiaohu. [V-SZZ: automatic identification of version ranges affected by CVE vulnerabilities](https://doi.org/10.1145/3510003.3510113). Proceedings of the 44th International Conference on Software Engineering. (2022).

  * Challande, Alexis, David, Robin, and Renault, Gu\'{e}na\"{e}l. [Building a Commit-level Dataset of Real-world Vulnerabilities](https://doi.org/10.1145/3508398.3511495). Proceedings of the Twelfth ACM Conference on Data and Application Security and Privacy. (2022).

  * Nima Shiri Harzevili, Jiho Shin, Junjie Wang, and Song Wang. [Characterizing and Understanding Software Security Vulnerabilities in Machine Learning Libraries](https://arxiv.org/abs/2203.06502). arXiv. (2022).

  * Sonnekalb, Tim, Heinze, Thomas S., and M\"{a}der, Patrick. [Deep security analysis of program code: A systematic literature review](https://doi.org/10.1007/s10664-021-10029-x). Empirical Softw. Engg.. (2022).

  * Andrea Stefanoni, Sarunas Girdzijauskas, Christina Jenkins, Zekarias T. Kefato, Licia Sbattella, Vincenzo Scotti, and Emil W{\aa}reus. [Detecting Security Patches in Java Projects Using NLP Technology](https://api.semanticscholar.org/CorpusID:256739262). International Conference on Natural Language and Speech Processing. (2022).

  * Dejiang Jing. [Improvement of Vulnerable Code Dataset Based on Program Equivalence Transformation](https://dx.doi.org/10.1088/1742-6596/2363/1/012010). Journal of Physics: Conference Series. (2022).

  * Nguyen-Truong, Giang, Kang, Hong Jin, Lo, David, Sharma, Abhishek, Santosa, Andrew E., Sharma, Asankhaya, and Ang, Ming Yi. HERMES: Using Commit-Issue Linking to Detect Vulnerability-Fixing Commits. 2022 IEEE International Conference on Software Analysis, Evolution and Reengineering (SANER). (2022).

  * Aurora Papotti, Ranindya Paramitha, and Fabio Massacci. [On the acceptance by code reviewers of candidate security patches suggested by Automated Program Repair tools](https://arxiv.org/abs/2209.07211). arXiv. (2022).

  * Triet H. M. Le, and M. Ali Babar. [On the Use of Fine-grained Vulnerable Code Statements for Software Vulnerability Assessment Models](https://arxiv.org/abs/2203.08417). arXiv. (2022).

  * Chapman, Jon, and Venugopalan, Hari. Open Source Software Computed Risk Framework. 2022 IEEE 17th International Conference on Computer Sciences and Information Technologies (CSIT). (2022).

  * Gerardo Canfora, Andrea {Di Sorbo}, Sara Forootani, Matias Martinez, and Corrado A. Visaggio. [Patchworking: Exploring the code changes induced by vulnerability fixing activities](https://www.sciencedirect.com/science/article/pii/S0950584921001932). Information and Software Technology. (2022).

  * Coskun, Tugce, Halepmollasi, Rusen, Hanifi, Khadija, Fouladi, Ramin Fadaei, De Cnudde, Pinar Comak, and Tosun, Ayse. [Profiling developers to predict vulnerable code changes](https://doi.org/10.1145/3558489.3559069). Proceedings of the 18th International Conference on Predictive Models and Data Analytics in Software Engineering. (2022).

  * Reis, Sofia, Abreu, Rui, Erdogmus, Hakan, and P\u{a}s\u{a}reanu, Corina. [SECOM: towards a convention for security commit messages](https://doi.org/10.1145/3524842.3528513). Proceedings of the 19th International Conference on Mining Software Repositories. (2022).

  * Jianlei Chi, Yu Qu, Ting Liu, Qinghua Zheng, and Heng Yin. [SeqTrans: Automatic Vulnerability Fix via Sequence to Sequence Learning](https://arxiv.org/abs/2010.10805). arXiv. (2022).

  * Wang, Shichao, Zhang, Yun, Bao, Liagfeng, Xia, Xin, and Wu, Minghui. VCMatch: A Ranking-based Approach for Automatic Security Patches Localization for OSS Vulnerabilities. 2022 IEEE International Conference on Software Analysis, Evolution and Reengineering (SANER). (2022).

  * Sun, Qing, Xu, Lili, Xiao, Yang, Li, Feng, Su, He, Liu, Yiming, Huang, Hongyun, and Huo, Wei. VERJava: Vulnerable Version Identification for Java OSS with a Two-Stage Analysis. 2022 IEEE International Conference on Software Maintenance and Evolution (ICSME). (2022).

  * A. Dann, H. Plate, B. Hermann, S. Ponta, and E. Bodden. Identifying Challenges for OSS Vulnerability Scanners - A Study & Test Suite. IEEE Transactions on Software Engineering. (2022).

  * Arthur D. Sawadogo, Quentin Guimard, Tegawendé F. Bissyandé, Abdoul Kader Kaboré, Jacques Klein, and Naouel Moha. [Early Detection of Security-Relevant Bug Reports using Machine Learning: How Far Are We?](https://arxiv.org/abs/2112.10123). arXiv. (2021).

  * Sofia Reis, Rui Abreu, and Luis Cruz. [Fixing Vulnerabilities Potentially Hinders Maintainability](https://arxiv.org/abs/2106.03271). arXiv. (2021).

  * Rodrigo Andrade, and Vinícius Santos. [ Investigating vulnerability datasets](https://sol.sbc.org.br/index.php/vem/article/view/17213). Anais do IX Workshop de Visualização, Evolução e Manutenção de Software. (2021).

  * Lee, Jian Yi David  and       Chieu, Hai Leong. [Co-training for Commit Classification](https://aclanthology.org/2021.wnut-1.43). Proceedings of the Seventh Workshop on Noisy User-generated Text (W-NUT 2021). (2021).

  * Nikitopoulos, Georgios, Dritsa, Konstantina, Louridas, Panos, and Mitropoulos, Dimitris. [CrossVul: a cross-language vulnerability dataset with commit data](https://doi.org/10.1145/3468264.3473122). Proceedings of the 29th ACM Joint Meeting on European Software Engineering Conference and Symposium on the Foundations of Software Engineering. (2021).

  * Bhandari, Guru, Naseer, Amara, and Moonen, Leon. [CVEfixes: automated collection of vulnerabilities and their fixes from open-source software](http://dx.doi.org/10.1145/3475960.3475985). Proceedings of the 17th International Conference on Predictive Models and Data Analytics in Software Engineering. (2021).

  * Triet H. M. Le, David Hin, Roland Croft, and M. Ali Babar. [DeepCVA: Automated Commit-level Vulnerability Assessment with Deep Multi-task Learning](https://arxiv.org/abs/2108.08041). arXiv. (2021).

  * Ganz, Tom, H\"{a}rterich, Martin, Warnecke, Alexander, and Rieck, Konrad. [Explaining Graph Neural Networks for Vulnerability Discovery](https://doi.org/10.1145/3474369.3486866). Proceedings of the 14th ACM Workshop on Artificial Intelligence and Security. (2021).

  * Guanqun Yang, Shay Dineen, Zhipeng Lin, and Xueqing Liu. [Few-Sample Named Entity Recognition for Security Vulnerability Reports by Fine-Tuning Pre-Trained Language Models](https://arxiv.org/abs/2108.06590). arXiv. (2021).

  * Zhou, Jiayuan, Pacheco, Michael, Wan, Zhiyuan, Xia, Xin, Lo, David, Wang, Yuan, and Hassan, Ahmed E.. Finding A Needle in a Haystack: Automated Mining of Silent Vulnerability Fixes. 2021 36th IEEE/ACM International Conference on Automated Software Engineering (ASE). (2021).

  * Garg, Spandan, Moghaddam, Roshanak Zilouchian, Sundaresan, Neel, and Wu, Chen. [PerfLens: a data-driven performance bug detection and fix platform](https://doi.org/10.1145/3460946.3464318). Proceedings of the 10th ACM SIGPLAN International Workshop on the State Of the Art in Program Analysis. (2021).

  * Piran, Azin, Chang, Che-Pin, and Fard, Amin Milani. Vulnerability Analysis of Similar Code. 2021 IEEE 21st International Conference on Software Quality, Reliability and Security (QRS). (2021).

  * Marchand-Melsom, Alexander, and Nguyen Mai, Duong Bao. [Automatic repair of OWASP Top 10 security vulnerabilities: A survey](https://doi.org/10.1145/3387940.3392200). Proceedings of the IEEE/ACM 42nd International Conference on Software Engineering Workshops. (2020).

  * Arthur D. Sawadogo, Tegawendé F. Bissyandé, Naouel Moha, Kevin Allix, Jacques Klein, Li Li, and Yves Le Traon. [Learning to Catch Security Patches](https://arxiv.org/abs/2001.09148). arXiv. (2020).

  * Fan, Jiahao, Li, Yi, Wang, Shaohua, and Nguyen, Tien N.. [A C/C++ Code Vulnerability Dataset with Code Changes and CVE Summaries](https://doi.org/10.1145/3379597.3387501). Proceedings of the 17th International Conference on Mining Software Repositories. (2020).

  * Patrick Keller, Laura Plein, Tegawendé F. Bissyandé, Jacques Klein, and Yves Le Traon. [What You See is What it Means! Semantic Representation Learning of Code based on Visualization and Transfer Learning](https://arxiv.org/abs/2002.02650). arXiv. (2020).

  * Song Wang, and Nachi Nagappan. [Characterizing and Understanding Software Developer Networks in Security Development](https://arxiv.org/abs/1907.12141). arXiv. (2019).




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
