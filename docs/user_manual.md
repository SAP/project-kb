# User Manual

## Summary

This is the user manual of the `kaybee` tool, which is part of `project KB`.

**WARNING:** this document is *work in progress*. Some of the commands
mentioned below might not be fully implemented at this time.

Please refer to the output of `kaybee help` and `kaybee <command> help` to
know what flags and options are available.

## Commands

### `create`

The `create` command is used to create vulnerability statements.

### `pull`

The `pull` command is used to retrieve statements from remote sources to the local machine.

### `merge`

The `merge` command is used to aggregate (and possibly reconcile)
vulnerability statements coming from different sources.

### `import`

The `import` command is used to import vulnerability data from a
variety of services/formats, in particular from a Steady backend.

### `export`

The `export` command is used to export vulnerability statements to
multiple formats.

### `list`

*note*: this is still not implemented at this time (v0.6.5)

The `list` command is used to display the content of statement repositories (remote or local).


### `purge`

The `purge` command deletes all the local clones of remote sources that have not been
updated for longer than a specified amount of time. This command is used to ensure compliance
to data retention policies, and can be invoked, for example, as a recurrent scheduled job.

### `update`

The `update` command is used to check if a newer version of the tool is available, and if so, to update it.

### `version`

The `version` command is used to show detailed information about
the current version of `kaybee`.

## Configuration

*to be written*
