-- public.users definition

-- Drop table

DROP TABLE IF EXISTS public.users;

CREATE TABLE public.users (
	id varchar(40) NOT NULL PRIMARY KEY,
	hashed_password varchar(40) NOT NULL,
	firstname varchar NOT NULL,
	lastname varchar NULL,
	photo varchar NULL,
	account_created varchar NULL,
	last_access varchar NULL
);
