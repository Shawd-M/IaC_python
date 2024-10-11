# Programme de Configuration d'Hôtes Distants

## Objectif

Ce projet consiste à développer un programme en ligne de commande permettant de **configurer des hôtes distants** via le protocole SSH. Le projet est développé en **Python** et utilise plusieurs bibliothèques pour faciliter la gestion des connexions SSH, la création de templates, et l'interface en ligne de commande.

## Modules Utilisés

Les bibliothèques suivantes sont utilisées pour ce projet :

- **paramiko** : Un wrapper autour du protocole SSH pour gérer les connexions à distance.
- **jinja2** : Utilisé pour la gestion des templates lors de la configuration.
- **click** : Un wrapper pour créer des interfaces en ligne de commande de manière simple et intuitive.
- **docopt** : Gère les arguments et options passés en ligne de commande.
- **pyyaml** : Permet de lire et d'analyser les fichiers de configuration au format YAML.

## Fonctionnalités

- **Connexion SSH** : Utilisation de `paramiko` pour se connecter à des hôtes distants via SSH et exécuter des commandes.
- **Templates de Configuration** : Génération dynamique de fichiers de configuration à l'aide de templates Jinja2.
- **Interface CLI** : Création d'une interface utilisateur en ligne de commande avec `click` et `docopt` pour gérer les différentes options et commandes du programme.
- **Lecture de fichiers YAML** : Chargement et analyse des fichiers de configuration en format YAML avec `pyyaml`.

## Prérequis

- Python 3.x
- Les modules listés ci-dessus (installation via pip)
