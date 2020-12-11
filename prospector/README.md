# Using Machine-Learning and Natural Language Processing to Find Security-Fixes for Vulnerabilities in Open-Source Software Repositories.

## Thesis Result Daan Hommersom
Thesis done in partial fulfillment of the requirements for the degree of Master of Science in Data Science & Entrepreneurship at the Jheronimus Academy of Data Science during a graduation internship at SAP.

# Prospector
Prospector is a tool to reduce the effort needed in finding security fixes forvulnerabilities in open source software. Two interfaces have been developed where the user can provide the information; a command line interface, and a dashboard developed in StreamLit. If Prospector is used to look for fix commits for a vulnerability which is in the NVD, the user only needs to provide the vulnerability identifier (CVE) and Prospector will create a vulnerability statement automatically through the NVD API.

A data engineering pipeline has been created. After a vulnerability statement has been provided or created, Prospector automatically selects a subset of the commits in the repository (with 93.5 recall). For all these commits, the commit message, timestamp and the git diff are obtained through the git command line interface. This is then processed into more information as the paths changed files. Afterwards, commits that do not change at least one code file are discarded from this selection (e.g. commits that just change the documentation of the project), resulting in a set of commits we treat as candidates to be the fix commit.

For every candidate commit a ranking vector is created. This ranking vector is composed of multiple components that contain a numeric value, providing information on the candidate commit, such as the number of changed files and the lexical similarity with the vulnerability description. This ranking vector is then used to predict the probability of a ranking vector being the ranking vector of a fix commit, and sort the commits based on this probability score. The current model of Prospector is able to rank a fix commit in the top ten for 83 percent of the vulnerabilities.

## How to use

Through cloning this repository and installing requirements.txt (`pip install -r requirements.txt`), you should be able to use Prospector yourself. There are two options to run prospector:

 - Command line interface: `python main.py <vulnerability_id> `
 - StreamLit interface: `streamlit run prospector_interface.py`

### To provide by the user

For vulnerabilities that are in the NVD (CVEs), you only need to provide the CVE and the URL of the repository that is affected. For vulnerabilities that are not in the NVD, you will need to provide additional information. Furthermore, you can provide all values manually to improve the prediction.

### Database & git-explorer

Prospector uses a SQLite database to store commit content. When providing a vulnerability that affects a repository that is not in your database yet, the extraction of this content can take a while (approximately fifty minutes for one-thousand commits). The vulnerability information is also stored in a database, which is used to try to predict a repository URL for the affected project. However, this will only work well after you have added a large number of vulnerabilities do your database.