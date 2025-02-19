# Utiliser une image Python officielle comme base
FROM python:3.9

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de l'application
COPY . /app

# Installer les dépendances
RUN pip install flask

# Exposer le port de l'application
EXPOSE 5000

# Démarrer l'application Flask
CMD ["python", "app.py"]
