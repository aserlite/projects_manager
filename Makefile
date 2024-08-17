.DEFAULT_GOAL := help
.PHONY: help

help: ## Display help
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
# Commande par défaut pour lancer l'outil
up: ## Start
	@python projects_manager.py

start: up

purge: ## Remove all sites
	@echo "Tous les sites vont être supprimés, êtes-vous sûr? [Y/N]"; \
	read response; \
	if [ "$$response" = "Y" ] || [ "$$response" = "YES" ] || [ "$$response" = "y" ] || [ "$$response" = "yes" ] || [ "$$response" = "Yes" ]; then \
	  	ddev poweroff; \
		rm -Rf ./sites; \
	  	ddev poweroff; \
		mkdir sites; \
	fi

install-dependencies: ## Install dependencies
	pip install -r requirements.txt

install-certs: ## Install certificates
	@echo "Installation des certificats"
	@echo "Veuillez saisir le mot de passe de votre machine"
	@mkcert -install