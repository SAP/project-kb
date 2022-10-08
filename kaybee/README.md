# KayBee


## Install

Just [download a binary](https://github.com/SAP/project-kb/releases/latest) compatible with your
operating system, make sure it has execution permissions if applicable, and then
run it.

Optionally, for your convenience, you may want to make sure that the binary is
in your `$PATH`.

For example, in Linux you would put the following line in your `.bashrc` file:

    export PATH=$PATH:/usr/local/bin/kaybee

(please, make sure you adjust the path to the `kaybee` binary as necessary)

Alternatively, you can clone this repository and build it yourself (you will need `go` and `make`).
You can do so with the `make` command; inspecting the Makefile first is a good idea.

## Usage

Once you have downloaded or built the binary, you can see the list of supported
commands with:

`kaybee --help`


To import vulnerability data in Eclipse Steady, run the following command:

```kaybee pull```

This will retrieve all the statements from all the sources configured in your
`kaybeeconf.yaml` file.

You can then run:

```kaybee export --target steady```

to generate a script `steady.sh`; edit the top of the script to indicate the URL of
your Steady backend and change the other variables as you see fit (there are comments
in the file to guide you), then run it.
