## Ideas by SLAB

# Idea_1
The further development direction of Prospector could be to create a centralized
database containing the processed projects (parsed data). Instead of creating a
web UI and running git parsing on the remote server, the clients could run it
locally and upload their results, so in case a new client wants to run queries
on the same repository, the servers can send it for him. The process flow can be
better explained with Idea_1.png.

# Idea_2
The current bottleneck in Prospector runtime is parsing the .git folder to an
SQL database. We might take a look at other solutions, which parse .git folders
and try them and learn from them to improve the processing speed of this initial
step. Example project: https://github.com/src-d/gitbase
