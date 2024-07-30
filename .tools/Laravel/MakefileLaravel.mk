.DEFAULT_GOAL := help

# Raccourci pour exécuter les migrations
migrate:
	php artisan migrate

# Installation des dépendances
install:
	composer install

# Raccourci pour créer un nouveau modèle avec Filament
model:
	php artisan make:model

# Raccourci pour créer une nouvelle ressource avec Filament
resource:
	php artisan make:resource

# Raccourci pour créer un nouveau contrôleur avec Filament
controller:
	php artisan make:controller

# Raccourci pour créer un nouvel utilisateur avec Filament
user:
	php artisan filament:user

# Raccourci pour exécuter les tests PHPUnit
test:
	php artisan test

# Raccourci pour effacer le cache de l'application
clear-cache:
	php artisan cache:clear

# Raccourci pour effacer les fichiers journaux
clear-logs:
	php artisan log:clear

# Raccourci pour effacer le cache de la configuration
clear-config:
	php artisan config:clear

# Raccourci pour effacer la mise en cache des routes
clear-route-cache:
	php artisan route:clear

# Raccourci pour effacer le cache de la vue
clear-view-cache:
	php artisan view:clear

# Raccourci pour créer un nouveau rôle avec Filament
make-role:
	php artisan filament:role

# Afficher toutes les commandes avec leur utilité
help:
	@echo ""
	@echo "\033[1;32mCommandes disponibles :\033[0m"
	@echo ""
	@echo "  \033[1;32mmigrate\033[0m       : Exécuter les migrations"
	@echo "  \033[1;32minstall\033[0m       : Installation des dépendances"
	@echo "  \033[1;32mmodel\033[0m         : Créer un nouveau modèle avec Filament"
	@echo "  \033[1;32mresource\033[0m      : Créer une nouvelle ressource avec Filament"
	@echo "  \033[1;32mcontroller\033[0m    : Créer un nouveau contrôleur avec Filament"
	@echo "  \033[1;32muser\033[0m          : Créer un nouvel utilisateur avec Filament"
	@echo "  \033[1;32mmake-role\033[0m     : Créer un nouveau rôle avec Filament"
	@echo "  \033[1;32mtest\033[0m          : Exécuter les tests PHPUnit"
	@echo "  \033[1;32mclear-cache\033[0m   : Effacer le cache de l'application"
	@echo "  \033[1;32mclear-logs\033[0m    : Effacer les fichiers journaux"
	@echo "  \033[1;32mclear-config\033[0m  : Effacer le cache de la configuration"
	@echo "  \033[1;32mclear-route\033[0m   : Effacer la mise en cache des routes"
	@echo "  \033[1;32mclear-view\033[0m    : Effacer le cache de la vue"
	@echo ""
	@echo ""

