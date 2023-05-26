SHELL := /bin/sh

GREEN='[\033[0;32m'
YELLOW='[\033[1;33m'
END='\033[0m]'	# No Color
DONE="$(GREEN)DONE$(END)"
PROGRESS="$(YELLOW)....$(END)"


setup: requirements.txt
	@cp config-sample.yaml config.yaml
	@cp .env-sample .env
	@echo "$(PROGRESS) Installing requirements"
	@pip install -r requirements.txt
	@echo "$(DONE) Installed requirements"
	@echo "$(PROGRESS) Installing pre-commit and spacy model"
	@python -m spacy download en_core_web_sm
	@echo "$(DONE) Installed pre-commit and spacy model"

dev-setup: setup requirements-dev.txt
	@echo "$(PROGRESS) Installing development requirements"
	@pip install -r requirements-dev.txt
	@pre-commit install
	@echo "$(DONE) Installed development requirements"

docker-setup:
	docker build -t prospector-base:1.0 -f ./docker/Dockerfile .
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


clean:
	@rm -f prospector.log
	@rm -rf __pycache__
	@rm -rf */__pycache__
	@rm -rf */*/__pycache__
	@rm -rf *.log
	@rm -rf .pytest_cache
	@rm -rf *.html
	@rm -rf *.json
	@rm -rf *.sqlite
#@rm -rf $(GIT_CACHE)/*
