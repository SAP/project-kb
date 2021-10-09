# Getting started with project "KB"

## Installation

The installation of the `kaybee` tool consists in just downloading the appropriate
[binary for your operating system](https://github.com/SAP/project-kb/releases).
Make sure it is executable; you might want to also ensure that it is in the `$PATH`, for your convenience.

For example, in Linux you would put the following line in your `.bashrc` file:

    export PATH=$PATH:/usr/local/bin/kaybee

(please, make sure you adjust the path to the `kaybee` binary as necessary)

Alternatively, you can clone this repository and build it yourself (you will need `go` and `make`).
You can do so with the `make` command; inspecting the Makefile first is a good idea.

## Configuration

The operation of the `kaybee` command is controlled via a configuration file and with
command flags and switches (these take priority over the configuration).

To create a configuration file, just run `kaybee setup`; you will have to edit it manually
to make it work with your particular setup (for example, the Steady endpoint is set to a dummy value
in the default configuration file, you will need to change that to import data from a Steady backend).

The configuration file, by default, is called `kaybeeconf.yaml` and is searched for
in the current directory and, if it is not there, in your home.

You can put the file in any location (and give it a different name), and
instruct `kaybee` to use it with the global flag `-c`. For example:

    kaybee -c /path/to/your/configfile.yaml <command here...>

Editing such a configuration file is necessary because that's were you can specify the list
of sources from which you intend to retrieve vulnerability data from and
a few other things, the most important of which are covered in the following.

If you have just downloaded the tool, the easiest way to start configuring
it is to run:

    kaybee setup

which will create a template configuration file in the current folder. You
will need to edit it to tailor it to your needs (it contains extensive comments
to guide you). At the very least, you will need to configure one or more sources,
as in this example:

    sources:
    - repo: https://github.com/sap/project-kb
      branch: vulnerability-data
      rank: 10


## Retrieving vulnerability data

This is achieved with the command:

    kaybee pull

The result will be a local clone of each of the sources. You can
manually inspect their content and interact with them as with any
other cloned git repository (that is what they are after all).

Unless you only consume data from one source, this is not very useful
per se: things get more interesting when you use `kaybee` to merge
the content of different sources, which is covered next.

## Merging  vulnerability data

The idea underlying project "KB" is to allow multiple independent
parties to maintain their own vulnerability data repository, and then
to allow users to define how the data from these sources is to be aggregated
and reconciled.

This is achieved with the command:

    kaybee merge

Unless instructed otherwise, the `kaybee` command will apply a conservative
policy (called `strict`) which will not attempt to reconcile statements
that refer to the same vulnerability. This is still useful in practice if
the vulnerabilities covered by different sources are mostly distinct; also,
because this policy is very conservative, it is suitable for unattended
executions of the tool (say, in a cron job that pulls and merges vulnerability
data on a regular basis). Other policies are possible, and at the time of writing
(June 2020), an experimental `soft` policy is under development: this policy
will allow statements to be reconciled and their contents to be merged automatically
(under certain conditions).

The tool can be instructed to use a particular policy by setting the corresponding
option in the configuration file, or via the command line flag `-p`, as in:

    kaybee merge -p strict
    kaybee merge -p soft



## Exporting vulnerability data

The `kaybee export` command can be used to export statements to a number of formats.
For example, this command:

    kaybee export -t xml

or the equivalent:

    kaybee export --target xml

examines the content of the directory `.kaybee/merged`, which contains the results of
the last run of `kaybee merge` and exports the statements contained there to XML.

It is important to stress that the export capabilities of `kaybee` are very generic, and
allow users to write their own exporters to arbitrary text-based formats (called export `targets`, hence
the `-t` flag).

An example of a completely different export target is `steady`:

    kaybee export -t steady

or equivavalently:

    kaybee export --target steady

The result this time is a script (`steady.sh`) that can be executed to import
vulnerability data to an Eclipse Steady server.

To export a folder other than the default, one can use the `--from` option, like so:

    kaybee export --target steady --from /path/to/the/statements/you/wish/to/export


## Creating new vulnerability statements

You can use `kaybee create` to create a skeleton for you to edit.

Alternatively, you can take an existing statement as a reference, but this is more
tedious and error prone.

A `check` command is planned, to validate a statement. Also, a more user-friendly GUI-based wizard
will probably come later on.

## Publishing

*To be written....*
