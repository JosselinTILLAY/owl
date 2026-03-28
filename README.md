# OWL - AI Plugin for moodle
<img src="./owl green.png" alt="drawing" width="80px" style="clip-path: circle(40px);"/>

OWL est un plugin pour [Moodle](https://moodle.org), un LMS utilisé dans beaucoup d'écoles et université pour les cours à distance ou les cours avec un complément numérique (supports de cours, activités pdéagogiques, QCM, examens, etc.).

Grâce à OWL, vous pouvez générer avec l'IA du contenu complémentaire aux ressources pédagogiques existantes pour changer la manière d'apprendre.

Le plugin est pensé pour pouvoir être paramétrable par un administrateur du LMS en accord avec la politique de gestion de la confidentialité des données avec des modèles en API publique, en API privée, ou en local.

## Made by Hackers @ SHIFT 2026

Le SHIFT Hackathon 2026 a pour objectif d'ajouter une feature AI sur un produit qui existe déjà.

## Installation

Pour installer, vous pouver lancer `install.sh` mais il est nécessaire de faire quelques étapes à la main

``` bash
# install.sh
git clone -b MOODLE_501_STABLE git@github.com:moodle/moodle.git
cp config.php moodle/config.php
cp .env.example .env
```

Puis changez les valeurs dans votre `.env`

Lancement avec docker : `docker compose up -d`

### Setup moodle admin
Allez sur `http://localhost:8089` pour installer moodle et définir quelques paramètres obligatoires.

### Post installation
Pour le confort, vous pouvez installer le package de langue FR sur http://localhost:8089/admin/tool/langimport/index.php

## Moodle et l'IA

### Fonctionnalité IA dans moodle récent (5.1.x)
- On peut setup plusieurs instances de providers parmis : OpenAI, Azure AI, Deepseek et Ollama
- On peut ensuite décliner selon les usages génération texte, image, résumé de texte, les choix des modèles
- 100% orienté usage enseignant pour la préparation du cours, mais limité dans un contexte activité ou ressource (pas course-wide)
- Un suivi très léger des logs coté admin, mais sans détail, et encore moins les codes d'erreur.
- De nombreuses erreurs et la plupart sont du type "erreur, pas plus d'infos démerde toi"
- Une fonctionnalité de résumé de page éditeur ... qui explique que c'est un éditeur ... ok.
- Pas compatible custom API (instance étatique, etc.), ni Mistral, ni Claude, ni Perplexity, ni Gemini (bon ça c'ets normal, GCP ... Oauth2, toi même tu sais)
- Usage orentié copy paste (il y a quand même le insert)
- Acceptation politique IA (en gros moodle n'est pas responsable des datas que vous mettez dans les IA publiques)

### Ce qui n'existe pas :
- Génération Audio
- Génération Vidéo
- Choix multiple des ressources course-wide pour alimenter la génération


## License
OWL is under GNU General Public License v3.0  
[See more](./COPYING.txt)
