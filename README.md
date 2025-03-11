# - API SoftDesk

## Installation et exécution de l'application

1. Clonez ce dépôt de code à l'aide de la commande `git clone https://github.com/ThibaultGERARDIN/pythonProjet10.git`
2. Rendez-vous depuis un terminal à la racine du répertoire pythonProjet9 avec la commande `cd pythonProjet10`
3. Créez un environnement virtuel pour le projet avec `python -m venv env` sous windows ou `python3 -m venv env` sous macos ou linux.
4. Activez l'environnement virtuel avec `env/Scripts/activate` sous windows ou `source env/bin/activate` sous macos ou linux.
5. Si vous avez déjà installé poetry : installez les dépendances du projet avec la commande `poetry install`
Si Poetry n'est pas encore installé, suivez les instructions sur la documentation officielle : https://python-poetry.org/docs/
6. Entrez dans le dossier de l'application avec la commande `cd litrevu`
7. Pour initialiser la base de données et vous permettre de créer des objets tapez la commande `python manage.py makemigrations` et `python manage.py migrate`
8. Si vous le souhaitez vous pouvez créer un superuser (pour accéder à django-admin) en utilisant la commande `python manage.py createsuperuser`
9. Démarrez le serveur avec `python manage.py runserver`


Pour tester les différents endpoints vous pouvez utiliser l'outil Postman (ou tout autre outil équivalent).

Pour simplifier la découverte de l'API vous pouvez consulter la documentation créée à l'aide de postman : https://documenter.getpostman.com/view/33644475/2sAYk8thEY
