#!make

include .env

test:
	echo "TEST"

setup: requirements.txt
	python -m pip install -r requirements.txt
	mkdir -p $(GIT_CACHE)

dev-setup: requirements.txt requirements-dev.txt
	mkdir -p $(GIT_CACHE)
	mkdir -p $(CVE_DATA_PATH)
	python -m pip install -r requirements-dev.txt
	python -m pip install -r requirements.txt

docker-setup:
	mkdir -p $(GIT_CACHE)
	mkdir -p $(CVE_DATA_PATH)
	docker-compose up -d --build

docker-clean: docker-clean.sh
	bash docker-clean.sh

run: client/cli/main.py
	python client/cli/main.py CVE-2014-0050 --repository https://github.com/apache/commons-fileupload --use-nvd --tag-interval FILEUPLOAD_1_3:FILEUPLOAD_1_3_1

select-run:
	python client/cli/main.py $(cve) --repository $(repository) --use-nvd

clean:
	rm prospector-report.html
	rm -f all.log* error.log*
	rm -rf __pycache__