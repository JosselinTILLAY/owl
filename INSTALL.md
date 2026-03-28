# OWL - AI Plugin for moodle

## git clone moodle
`git clone -b MOODLE_501_STABLE git@github.com:moodle/moodle.git`

## Copy config.php
`cp config.php moodle/config.php`

## copy .env and set values 
`cp .env.example .env`

## Setup moodle admin
Go to `http://localhost:8089` to run the first setup, admin account

## Post installation
Pour le confort, vous pouvez installer le package de langue FR sur http://localhost:8089/admin/tool/langimport/index.php


### Fonctionnalité IA dans moodle récent (5.1)
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




