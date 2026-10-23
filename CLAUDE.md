# CLAUDE.md

Site GitHub Pages racine de `cedric167` (https://cedric167.github.io/). Aucune étape de build : les fichiers sont servis tels quels.

## Contenu

- `index.html` : redirection immédiate vers https://cedric167.github.io/litefoil-tracker/ (le site de l'appli vit dans un autre dépôt).
- `.well-known/assetlinks.json` : Digital Asset Links qui lient l'appli Android « Lite Foil Tracker » (`fr.litefoil.tracker`) au domaine.
- `.nojekyll` : désactive Jekyll, sinon GitHub Pages ne publierait pas le dossier `.well-known`. Ne pas le supprimer.

## Règles

- `assetlinks.json` doit rester un JSON valide. Une erreur casse l'ouverture des liens dans l'appli Android. Vérifier avec `python3 -m json.tool .well-known/assetlinks.json`.
- Les empreintes `sha256_cert_fingerprints` sont celles de la clé d'upload et de la clé Play App Signing. Ne jamais en retirer une sans demande explicite.
- Messages de commit en français.
