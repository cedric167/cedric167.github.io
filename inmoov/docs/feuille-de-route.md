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

## Étape 5 : base mobile sur hoverboard

On commence seulement quand le robot complet est stable sur un socle fixe. Le hoverboard n'est pas utilisé en gyropode : ses deux roues motorisées sont fixées sur un châssis avec une ou deux roulettes folles, ce qui donne une base qui ne bascule pas.

À prévoir :
- un hoverboard d'occasion, avec sa carte mère d'origine et une batterie en bon état ;
- un programmateur ST-Link V2 ;
- un adaptateur USB-série 3,3 V, pour relier la carte du hoverboard au portable ;
- un châssis en profilé alu ou contreplaqué épais, et 1 à 2 roulettes folles ;
- 3 à 4 capteurs ultrasons ou un petit lidar, plus une carte Arduino Nano ;
- un deuxième bouton d'arrêt d'urgence, ou un bouton à plus de contacts.

Les étapes :
- [ ] Reprogrammer la carte avec le firmware libre [hoverboard-firmware-hack-FOC](https://github.com/EmanuelFeru/hoverboard-firmware-hack-FOC), en variante de commande par liaison série (UART). Faire un essai roues en l'air, avec une vitesse maximale basse dans la configuration.
- [ ] Construire le châssis : centre de gravité bas, robot fixé solidement, batterie et portable bien calés.
- [ ] Câbler l'arrêt d'urgence pour qu'il coupe aussi le courant des moteurs, pas seulement celui des servos.
- [ ] Ajouter les capteurs d'obstacles. Ils arrêtent les roues en local, sans attendre Claude. C'est un réflexe, comme le suivi du visage.
- [ ] Ajouter au programme Python un module `base.py`, et donner à Claude des outils avec des limites : « avancer » (distance plafonnée), « reculer », « tourner » (angle), « s'arrêter ».
- [ ] Plafonner la vitesse à celle d'une marche lente (environ 0,5 m/s). Couper les roues si le programme ne reçoit plus d'ordre pendant une seconde.
- [ ] Premiers essais dans une pièce dégagée, la main sur l'arrêt d'urgence.

## Étape 6 : autonomie

- [ ] Ajouter des gestes dans `cerveau/inmoov/gestes.py`
- [ ] Affiner les consignes de Claude dans `cerveau/inmoov/cerveau_ia.py`
- [ ] Idées : prendre un objet simple, reconnaître les habitués (souvenirs), mode « accueil » qui démarre quand un visage apparaît, aller vers la personne qui l'appelle (base mobile)
