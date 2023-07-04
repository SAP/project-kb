-- public.processed_vuln definition

-- Drop table

DROP TABLE IF EXISTS public.processed_vuln;

CREATE TABLE public.processed_vuln (
    _id SERIAL PRIMARY KEY,
	fk_vulnerability INT NOT NULL UNIQUE,
    repository varchar NOT NULL,
    versions varchar,
    FOREIGN KEY (fk_vulnerability) REFERENCES public.vulnerability (_id)
);
