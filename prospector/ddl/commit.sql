-- public.commits definition

-- Drop table

DROP TABLE public.commits;

CREATE TABLE public.commits (
	id varchar(40) NOT NULL,
	repository varchar NOT NULL,
	feature_1 varchar NULL,
	feature_2 varchar NULL,
	timestamp text NULL,
	message varchar NULL,
	changed_files varchar NULL,
	diff varchar NULL,
	hunks varchar NULL,
	commit_message_reference_content varchar NULL,
	preprocessed_message varchar NULL,
	preprocessed_diff varchar NULL,
	preprocessed_changed_files varchar NULL,
	preprocessed_commit_message_reference_content varchar NULL,
	CONSTRAINT commits_pkey PRIMARY KEY (id, repository)
);
CREATE INDEX IF NOT EXISTS commit_index ON public.commits USING btree (id);
CREATE UNIQUE INDEX IF NOT EXISTS commit_repository_index ON public.commits USING btree (id, repository);
CREATE INDEX IF NOT EXISTS repository_index ON public.commits USING btree (repository);
