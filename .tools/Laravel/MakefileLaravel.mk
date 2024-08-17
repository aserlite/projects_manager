.DEFAULT_GOAL := help
.PHONY: help

migrate: ## Raccourci pour exécuter les migrations
	php artisan migrate

install: ## Installation des dépendances
	composer install

model: ## Raccourci pour créer un nouveau modèle avec Filament
	php artisan make:model

resource: ## Raccourci pour créer une nouvelle ressource avec Filament
	php artisan make:resource

controller: ## Raccourci pour créer un nouveau contrôleur avec Filament
	php artisan make:controller

user: ## Raccourci pour créer un nouvel utilisateur avec Filament
	php artisan filament:user

test: ## Raccourci pour exécuter les tests PHPUnit
	php artisan test

clear-cache: ## Raccourci pour effacer le cache de l'application
	php artisan cache:clear

clear-logs: ## Raccourci pour effacer les fichiers journaux
	php artisan log:clear

clear-config: ## Raccourci pour effacer le cache de la configuration
	php artisan config:clear

clear-route-cache: ## Raccourci pour effacer la mise en cache des routes
	php artisan route:clear

clear-view-cache: ## Raccourci pour effacer le cache de la vue
	php artisan view:clear

make-role: ## Raccourci pour créer un nouveau rôle avec Filament
	php artisan filament:role

help: ## Display help
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
