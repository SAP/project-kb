-- public.job definition

-- Drop table

DROP TABLE IF EXISTS public.job;

CREATE TABLE public.job (
	_id varchar NOT null PRIMARY KEY,
    pv_id  INT,
    params varchar NOT NULL,
    enqueued_at timestamp,
    started_at timestamp,
    finished_at timestamp,
    results varchar,
    created_by varchar,
    created_from varchar,
    status varchar,
    FOREIGN KEY (pv_id) REFERENCES public.processed_vuln (_id),
    FOREIGN KEY (created_from) REFERENCES public.job (_id)
);
