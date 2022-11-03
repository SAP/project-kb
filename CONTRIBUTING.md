# How to contribute to project KB

### Developer Certificate of Origin (DCO)
Due to legal reasons, contributors will be asked to accept a DCO when they create the first pull request to this project. This happens in an automated fashion during the submission process. SAP uses [the standard DCO text of the Linux Foundation](https://developercertificate.org/).

### **Do you have new vulnerability data?**

A structured process to create and share vulnerability data is work in progress.

Until it is defined, we invite you to just create pull requests in order to
submit new vulnerability data, using an existing statement as a template. You
should provide, at least the vulnerability identifier, the URL of the source
code repository of the affected component and one or more identifiers of the
commits used to fix the vulnerability.

### **Did you find a bug?**

* **Ensure the bug was not already reported** by searching in the [GitHub Issues](https://github.com/sap/project-kb/issues).

* If it is a new one, feel free to [open it](https://github.com/sap/project-kb/issues/new). Be sure to include a
  **title and a clear description**, as much relevant information as possible, and
  a **code sample** or an **executable test case** demonstrating the expected
  behavior that is not occurring.


### **Did you write a patch that fixes a bug?**

* Open a new GitHub pull request with the patch.
* Ensure the PR description clearly describes problem and solution. Include
  the relevant issue number if applicable.
* Add one or more test cases as appropriate.
* Make sure all other tests and checks still pass (that is, run `make check` in
  the `kaybee` folder; it should succeed)

### **Did you fix whitespace, format code, or make a purely cosmetic patch?**

Changes that are cosmetic in nature and do not modify the
stability, functionality, or testability are accepted.

### **Do you intend to add a new feature or change an existing one?**

* Suggest your change by creating an issue, then start writing code in your own
  fork and make a PR when ready. Please make sure you provide tests for your
  code, and ensure you can successfully execute `make check` (in the `kaybee`
  folder) with no errors and that you include adequate documentation in your
  code.


### **Do you have questions about the source code?**

* For now, file an issue (we consider that the need of clarifications at this
  stage indicates missing or inadequate documentation).

### **Do you want to contribute to the documentation?**

You are most welcome to do so, project KB needs every one of you to succeed,
every drop matters!

Thanks! :heart: :heart: :heart:

The project KB team
