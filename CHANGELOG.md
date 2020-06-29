# Changelog (`kaybee` tool)

<a name="v"></a>
## [v](https://github.com/sap/project-kb/compare/v0.6.3...v)

### Chores
 * scripts to automate release ([a931e50](https://github.com/sap/project-kb/commit/a931e50))

<a name="v"></a>
## [v](https://github.com/sap/project-kb/compare/v0.6.3...v)

### Chores
 * scripts to automate release ([a931e50](https://github.com/sap/project-kb/commit/a931e50))

<a name="v0.6.3"></a>
## [v0.6.3](https://github.com/sap/project-kb/compare/v0.6.2...v0.6.3)

### Bugfixes
 * setup cmd works (using pkger), fixes: #17 ([8ddb881](https://github.com/sap/project-kb/commit/8ddb881))

### Changes
 * create cmd now takes vulnID in input ([7478c80](https://github.com/sap/project-kb/commit/7478c80))

### Chores
 * better changelog generation (with links to commits) ([b55374a](https://github.com/sap/project-kb/commit/b55374a))

<a name="v0.6.2"></a>
## [v0.6.2](https://github.com/sap/project-kb/compare/v0.6.1...v0.6.2)

### Chores
 * add changelog generation script ([18f675c](https://github.com/sap/project-kb/commit/18f675c))
 * update deps for update cmd ([39d04cd](https://github.com/sap/project-kb/commit/39d04cd))

<a name="v0.6.1"></a>
## [v0.6.1](https://github.com/SAP/project-kb/compare/v0.6.0.2...v0.6.1) (2020-06-26)

feat: command to check if new release exists

<a name="v0.6.0.2"></a>
## [v0.6.0.2](https://github.com/SAP/project-kb/compare/v0.6.0.1...v0.6.0.2) (2020-06-26)

* fix: force creation of config file with -f flag (for real this time :-))

<a name="v0.6.0.1"></a>
## [v0.6.0.1](https://github.com/SAP/project-kb/compare/v0.6.0...v0.6.0.1) (2020-06-26)

* fix: force creation of config file with -f flag
* fix: build step,  install packr

<a name="v0.6.0"></a>
## [v0.6.0](https://github.com/SAP/project-kb/compare/v0.5.4.3...v0.6.0) (2020-06-26)

* fix: include template config file for setup cmd
* fix: (export) use output filename as configured
* new: export fix metadata in json format

### BREAKING CHANGES
The format of the metadata files produced by the steady script (obtained with
kaybee export -t steady) is now json.


<a name="v0.5.4.3"></a>
## [v0.5.4.3](https://github.com/SAP/project-kb/compare/v0.5.4.2...v0.5.4.3) (2020-06-26)

* set default concurrency to 1
* update changelog generation config

<a name="v0.5.4.2"></a>
## [v0.5.4.2](https://github.com/SAP/project-kb/compare/v0.5.4.1...v0.5.4.2) (2020-06-26)

* bug in import command (#15)

<a name="v0.5.4.1"></a>
## [v0.5.4.1](https://github.com/SAP/project-kb/compare/v0.5.4...v0.5.4.1) (2020-06-26)

* fix: broken `version` command (#14)

<a name="v0.5.4"></a>
## [v0.5.4](https://github.com/SAP/project-kb/compare/v0.5.3...v0.5.4) (2020-06-25)

* fix: add '//' at the end of backend url if missing
* added some real vulnerability statements

<a name="v0.5.3"></a>
## [v0.5.3](https://github.com/SAP/project-kb/compare/v0.5.2...v0.5.3) (2020-06-24)

* fix: setup command does not require a config file to exist
* new: initial documentation

<a name="v0.5.2"></a>
## [v0.5.2](https://github.com/SAP/project-kb/compare/v0.5.1...v0.5.2) (2020-06-24)

* fix allow backend to be set via command line flag (-b)
* fix source url in sample conf file
* fix broken link to binary downloads

<a name="v0.5.1"></a>
## [v0.5.1](https://github.com/SAP/project-kb/compare/2019-05-10...v0.5.1) (2020-06-22)

**Note: this is the first open-source version of the tool**

- "strict" merge policy
- initial implementation of "soft" merge policy
- import from Steady
- export to arbitrary text formats, using customizable templates
    - in particular: export to bash script that then imports to Steady
