# Getting started with project "KB"

## Installation and configuration of the kaybee tool

The installation of kaybee consists in just downloading the appropriate
binary for your operating system and making sure it is executable.
You might want to also ensure that it is in the path, for your convenience.

The configuration is necessary because it allows you to specify the list
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
    branch: master
    rank: 10

TO BE CONTINUED....