.DEFAULT_GOAL := up
.PHONY: up

# Commande par défaut pour lancer l'outil
up: ## Start
	@python3 projects_manager.py

start: up