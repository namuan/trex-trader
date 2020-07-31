export PROJECTNAME=$(shell basename "$(PWD)")
export REMOTEDIR=${PROJECTNAME}-v1

.SILENT: ;               # no need for @

venv: ## Setup Virtual Env
	python3 -m venv venv
	./venv/bin/pip install -r requirements.txt

deps: ## Install dependencies
	./venv/bin/pip install -r requirements.txt

lint: clean ## Runs black for code formatting
	./venv/bin/black bot common config exchanges --exclude generated

requirements: ## Sets up required dependencies
	./venv/bin/pip install -r requirements.txt

clean: ## Cleans all cached files
	find . -type d -name '__pycache__' | xargs rm -rf

deployapp: clean ## Deploy application
	ssh ${PROJECTNAME} -C "mkdir -vp ./${REMOTEDIR}"
	rsync -avzr \
				env.cfg \
				exchanges \
				config \
				bot \
				common \
				scripts \
				requirements.txt \
				telegram-trex-trader.py \
				${PROJECTNAME}:./${REMOTEDIR}/

ssh: ## ssh into project server
	ssh ${PROJECTNAME}

restart: ## Restarts supervisor
	ssh ${PROJECTNAME} -C "sh scripts/start_screen.sh telegram-trex-trader \"cd ${REMOTEDIR}; python3.6 telegram-trex-trader.py\""

run: lint ## Runs the bot locally
	./venv/bin/python3 telegram-trex-trader.py

.PHONY: help
.DEFAULT_GOAL := help

help: Makefile
	echo
	echo " Choose a command run in "$(PROJECTNAME)":"
	echo
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
	echo
