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
	python client/cli/main.py CVE-2022-29599 --repository https://github.com/apache/maven-shared-utils --use-nvd --tag-interval maven-shared-utils-3.2.0:maven-shared-utils-3.3.3

select-run:
	python client/cli/main.py $(cve) --repository $(repository) --use-nvd

clean:
	rm prospector-report.html
	rm -f all.log* error.log*
	rm -rf __pycache__