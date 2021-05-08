export PROJECTNAME=$(shell basename "$(PWD)")
export REMOTEDIR=${PROJECTNAME}-v1

.SILENT: ;               # no need for @

setup: ## Setup Virtual Env
	python3 -m venv venv
	./venv/bin/pip3 install -r requirements/dev.txt

deps: ## Install dependencies
	./venv/bin/pip3 install -r requirements/dev.txt

lint: ## Run black for code formatting
	./venv/bin/black . --exclude venv

clean: ## Clean package
	find . -type d -name '__pycache__' | xargs rm -rf
	rm -rf build dist

bpython: ## Run bpython
	./venv/bin/bpython

deployapp: clean ## Deploy application
	ssh ${PROJECTNAME} -C "mkdir -vp ./${REMOTEDIR}"
	rsync -avzr \
				env.cfg \
				exchanges \
				config \
				bot \
				common \
				scripts \
				requirements \
				telegram-trex-trader.py \
				${PROJECTNAME}:./${REMOTEDIR}/

ssh: ## ssh into project server
	ssh ${PROJECTNAME}

start: deployapp ## Restarts supervisor
	ssh ${PROJECTNAME} -C 'bash -l -c "./${REMOTEDIR}/scripts/setup_apps.sh ${REMOTEDIR}"'

stop: deployapp ## Stop any running screen session on the server
	ssh ${PROJECTNAME} -C 'bash -l -c "./${REMOTEDIR}/scripts/stop_apps.sh ${REMOTEDIR}"'


local: lint ## Runs the bot locally
	./venv/bin/python3 telegram-trex-trader.py

.PHONY: help
.DEFAULT_GOAL := help

help: Makefile
	echo
	echo " Choose a command run in "$(PROJECTNAME)":"
	echo
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
	echo
