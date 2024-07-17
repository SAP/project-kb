-- public.commit alteration

-- add column to save commit's relevance

ALTER TABLE public.commits
ADD security_relevant boolean NULL;