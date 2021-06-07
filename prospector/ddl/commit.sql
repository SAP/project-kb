-- public.commits definition

-- Drop table

DROP TABLE IF EXISTS public.commits;
CREATE TABLE public.commits (
	commit_id varchar(40) NOT NULL,
	repository varchar NOT NULL,
	timestamp int,
	-- preprocessed data
	hunks varchar[] NULL,
	hunk_count int,
	message varchar NULL,
	diff varchar[] NULL,
	changed_files varchar[] NULL,
	message_reference_content varchar[] NULL,
	jira_refs varchar[] NULL,
	ghissue_refs varchar[] NULL,
	cve_refs varchar[] NULL,
	tags varchar[] NULL,
	CONSTRAINT commits_pkey PRIMARY KEY (commit_id, repository)
);
CREATE INDEX IF NOT EXISTS commit_index ON public.commits USING btree (commit_id);
CREATE UNIQUE INDEX IF NOT EXISTS commit_repository_index ON public.commits USING btree (commit_id, repository);
CREATE INDEX IF NOT EXISTS repository_index ON public.commits USING btree (repository);
