SHELL := /bin/sh
include .env

GREEN='[\033[0;32m'
YELLOW='[\033[1;33m'
END='\033[0m]'	# No Color
DONE="$(GREEN)DONE$(END)"
PROGRESS="$(YELLOW)....$(END)"

test:
	@echo "$(PROGRESS) TEST"
	@echo "$(DONE) TEST"

setup: requirements.txt
	@echo "$(PROGRESS) Installing requirements"
	pip install -r requirements.txt
	@echo "$(DONE) Installed requirements"
	@echo "$(PROGRESS) Installing pre-commit and other modules"
	@pre-commit install
	@python -m spacy download en_core_web_sm
	@echo "$(DONE) Installed pre-commit and other modules"
	@mkdir -p $(GIT_CACHE)
	@echo "$(DONE) Created directory $(GIT_CACHE)"

dev-setup: setup requirements-dev.txt
	@mkdir -p $(CVE_DATA_PATH)
	@echo "$(DONE) Created directory $(CVE_DATA_PATH)"
	@echo "$(PROGRESS) Installing development requirements"
	pip install -r requirements-dev.txt
	@echo "$(DONE) Installed development requirements"

docker-setup:
	mkdir -p $(GIT_CACHE)
	mkdir -p $(CVE_DATA_PATH)
	docker-compose up -d --build

docker-clean:
	@echo "$(PROGRESS) Stopping and removing all container and images"
	@docker-compose down --rmi all -v 2>/dev/null
	@echo "$(DONE) Stopped and removed all container and images"

	@echo "$(PROGRESS) Cleaning volumes"
	@docker volume prune -f
	@echo "$(DONE) Cleaned volumes"

	@echo "$(PROGRESS) Cleaning residue"
	@docker system prune -a -f
	@echo "$(DONE) Cleaned residue"

run: client/cli/main.py
#python client/cli/main.py CVE-2014-0050 --repository https://github.com/apache/commons-fileupload --use-nvd --tag-interval FILEUPLOAD_1_3_RC1:FILEUPLOAD_1_3_2_RC1
	python client/cli/main.py CVE-2022-29599 --repository https://github.com/apache/maven-shared-utils --use-nvd
#--tag-interval maven-shared-utils-0.1:maven-shared-utils-3.3.4

select-run:
	python client/cli/main.py $(cve) --repository $(repository) --use-nvd

clean:
	rm prospector-report.html
	rm -f all.log* error.log*
	rm -rf $(GIT_CACHE)/*
	rm -rf __pycache__