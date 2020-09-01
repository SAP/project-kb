# How to contribute to project "KB"

#### **Do you intend to contribute with new vulnerability data?**

A structured process to create and share vulnerability data is work in progress.

For the time being, you can use `kaybee create <VULN.ID>` to generate a skeleton
statement that you can then edit with a normal text editor.

You can then create pull requests against the `vulnerability-data` branch in this repository
or you can host the statements in your own repository (please do let us know if you choose
this option so that we can benefit from your work by pulling your statements).

You will need to dedicate a branch to the statements: the branch must contain a
top-level `statements` folder in which you can store your statements. You can
refer to the [`vulnerability-data` branch in this
repository](https://github.com/SAP/project-kb/tree/vulnerability-data) to see
what is the expected structure.

Your statement should provide, at least, a vulnerability identifier (use the CVE
identifier if it exists), the URL of the source code repository of the affected
component and one or more identifiers of the commits used to fix the
vulnerability.

#### **Did you find a bug?**

* **Ensure the bug was not already reported** by searching on GitHub under [Issues](https://github.com/sap/project-kb/issues).

* If you're unable to find an open issue addressing the problem, [open a new one](https://github.com/sap/project-kb/issues/new). Be sure to include a **title and clear description**, as much relevant information as possible, and a **code sample** or an **executable test case** demonstrating the expected behavior that is not occurring.


#### **Did you write a patch that fixes a bug?**

* Open a new GitHub pull request with the patch.
* Ensure the PR description clearly describes the problem and solution. Include the relevant issue number if applicable.
* Add one or more test cases as appropriate
* Make sure all other tests and checks still pass (that is, run `make check` in the `kaybee` folder; it should succeed)

#### **Did you fix whitespace, format code, or make a purely cosmetic patch?**

Changes that are cosmetic in nature and do not add anything substantial to the stability, functionality, or testability are accepted at this time.

#### **Do you intend to add a new feature or change an existing one?**

* Suggest your change by creating an issue  and start writing code in your own fork and make a PR when ready.
Please make sure you provide tests for your code, and ensure you can successfully execute `make check` (in the `kaybee` folder)
with no errors and that you include adequate documentation in your code.




#### **Do you have questions about the source code?**

* For now, file an issue (we consider that the need of clarifications at this stage indicates missing or inadequate documentation).

#### **Do you want to contribute to the documentation?**

You are most welcome to do so, project "KB" needs every one of you to succeed, every drop matters!

Thanks! :heart: :heart: :heart:

The project "KB" team
