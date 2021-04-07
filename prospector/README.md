# Prospector

## What is it
Prospector is a tool to reduce the effort needed to find security fixes for
*known* vulnerabilities in open source software. Its approach is described in
more detail in this document: https://arxiv.org/pdf/2103.13375.pdf

The document can be cited as follows:
```
@misc{hommersom2021mapping,
    title = {Automated Mapping of Vulnerability Advisories onto
    their Fix Commits in Open Source Repositories},
    author = {Hommersom, Daan and
    Sabetta, Antonino and
    Coppola, Bonaventura and
    Tamburri, Damian A. },
    year = {2021},
    month = {March},
    url = {https://arxiv.org/pdf/2103.13375.pdf}
}
```

The first proof-of-concept was implemented by Daan Hommersom during his
internship at SAP Security Research for his Master thesis in Data Science &
Entrepreneurship at the Jheronimus Academy of Data Science.

The original code developed by Daan Hommersom [can be retrieved
here](https://github.com/SAP/project-kb/tree/d93b1c3ab47cb4d7ad7537c11a468580dabaf77d/prospector)
or through the tag `DAAN_HOMMERSOM_THESIS`.

This folder is kept as a placeholder, while a reimplementation of the tool
is progressing (see below).

**WARNING**
*Please understand that this implementation is a proof-of-concept
whose goal was to explore and validate a few research ideas:
feel free to try it out, but do expect some rough edges.*

## Complete reimplementation of Prospector is underway

At this time, a complete *reimplementation* is underway in the context of
the **[AssureMOSS](https://assuremoss.eu)** EU-funded project. The
work-in-progress is kept in the `assuremoss-prospector` branch, as well as
in the issues tagged as `assuremoss`.

Anyone interested in contributing to this activity is welcome: please take a
look at the open issues, and feel free to participate starting from there.

