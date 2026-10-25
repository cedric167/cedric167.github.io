# Feuille de route

Chaque étape donne un robot qui fonctionne déjà un peu mieux que la précédente. On ne passe à la suivante que quand la précédente marche.

## Étape 0 : le cerveau sans corps (1 soirée)

- [ ] Installer Python 3.10 ou plus récent sur le portable
- [ ] Créer la clé API Claude, la mettre dans `cerveau/.env`
- [ ] `python -m pytest` passe
- [ ] `python main.py --simulation --texte` : discuter avec le robot, lui demander de saluer, de regarder (webcam du portable)

## Étape 1 : main et avant-bras droits

- [ ] Imprimer la main et l'avant-bras droits (voir `impression.md`)
- [ ] Monter les 5 servos des doigts et celui du poignet, tendre les fils des doigts
- [ ] Câbler l'Arduino Mega + la première carte PCA9685 + l'alimentation + l'arrêt d'urgence (`cablage.md`)
- [ ] Téléverser `firmware/inmoov_servos` depuis l'IDE Arduino
- [ ] **Calibrer** chaque doigt : trouver à la main l'angle main ouverte / main fermée sans forcer, et le reporter en `min`/`max` dans `config.yaml`
- [ ] `python main.py --texte --sans-camera` : « ferme la main », « ouvre la main »

## Étape 2 : tête, yeux et mâchoire

- [ ] Imprimer et monter la tête, le cou, la mâchoire, le mécanisme des yeux
- [ ] Caméra USB dans l'œil (régler `camera:` dans `config.yaml`)
- [ ] Calibrer `tete_rotation`, `cou`, `machoire`, `yeux_*`
- [ ] Régler le suivi de visage : si la tête part dans le mauvais sens, inverser le signe de `gain_horizontal` ou `gain_vertical`
- [ ] Micro + haut-parleur : `python main.py` (la mâchoire bouge quand il parle)

## Étape 3 : bras droit complet

- [ ] Biceps, rotation, épaule, omoplate
- [ ] Calibration très prudente : ces servos sont puissants
- [ ] Tester les gestes `saluer`, `tendre_la_main`, `pointer_devant`

## Étape 4 : torse et bras gauche

- [ ] Torse, ventre, support (le robot ne tient pas debout seul : prévoir un socle solide, éventuellement à roulettes avec freins)
- [ ] Deuxième carte PCA9685 (adresse 0x41) pour le bras gauche et le torse
- [ ] Emplacement du portable sur le dos ou le socle, avec aération

## Étape 5 : autonomie

- [ ] Ajouter des gestes dans `cerveau/inmoov/gestes.py`
- [ ] Affiner les consignes de Claude dans `cerveau/inmoov/cerveau_ia.py`
- [ ] Idées : prendre un objet simple, reconnaître les habitués (souvenirs), mode « accueil » qui démarre quand un visage apparaît
