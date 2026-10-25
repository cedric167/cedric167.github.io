# Feuille de route

Chaque étape donne un robot qui fonctionne déjà un peu mieux que la précédente. On ne passe à la suivante que quand la précédente marche.

## Étape 0 : le cerveau sans corps (1 soirée)

- [ ] Installer **Ubuntu 24.04 LTS** sur le portable (nécessaire pour la navigation de l'étape 7 ; autant partir dessus dès le début), puis Python 3.10 ou plus récent
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

## Étape 5 : tablette sur le torse et appels WhatsApp

Une tablette Android fixée sur le torse sert aux appels visio et audio des clients. Claude reçoit la demande à la voix et commande la tablette depuis le portable par câble USB (ADB, l'outil de débogage d'Android). Pendant l'appel, Claude n'écoute plus et ne regarde plus : la conversation reste privée.

Deux façons d'appeler, au choix du client :
- **Option A, « avec mon WhatsApp »** : le client relie son propre compte à la tablette (WhatsApp → Appareils connectés → scanner le QR code affiché par la tablette), appelle un de ses contacts, puis la tablette se déconnecte et **efface tout**.
- **Option B, « depuis le robot »** : le client dicte le numéro de son contact, et la tablette l'appelle depuis le compte WhatsApp du robot, avec son numéro dédié.

À prévoir : la tablette et son support, un câble USB long, une SIM ou un numéro dédié pour le compte du robot (voir `materiel.md`, section 11).

Vérifications sur la vraie tablette, avant d'écrire le code :
- [ ] Activer le mode développeur et le débogage USB sur la tablette, et vérifier que `adb devices` la voit depuis le portable.
- [ ] Option B : installer WhatsApp avec le numéro du robot. Ajouter un contact de test et vérifier qu'une commande ADB peut lancer un appel vidéo et un appel audio vers lui.
- [ ] Option A : vérifier que la tablette peut être reliée comme appareil connecté, et que les appels vidéo et audio y fonctionnent.
- [ ] Option A : vérifier comment lancer l'appel. Les contacts d'un compte relié ne sont sans doute pas visibles par Android : il est probable que le client doive toucher lui-même le bouton d'appel sur l'écran, guidé à la voix par le robot.
- [ ] Vérifier qu'on peut raccrocher et revenir à l'écran d'accueil par ADB.
- [ ] Option A : vérifier que l'effacement complet (`adb shell pm clear` sur WhatsApp) déconnecte bien le compte du client. Le client doit voir la tablette disparaître de ses appareils connectés.

Programme (une fois les vérifications faites) :
- [ ] Module `cerveau/inmoov/telephone.py` qui commande la tablette par ADB.
- [ ] Nouveaux outils pour Claude : `appel_video`, `appel_audio`, `raccrocher`, `session_whatsapp_client` (démarre l'option A et affiche le QR code), `fin_session_client`.
- [ ] Option B : un client ne peut appeler qu'un numéro qu'il dicte lui-même. Le robot répète le numéro et attend une confirmation avant d'appeler. Prévoir une limite d'appels par heure et une liste de numéros interdits (numéros surtaxés, numéros étrangers si besoin).
- [ ] Option A : effacement automatique à la fin de l'appel, quand le client dit au revoir, et après quelques minutes sans activité.
- [ ] Mode « accueil client » : Claude ne note aucun souvenir sur les clients.
- [ ] Le micro et la caméra du robot sont coupés pour Claude pendant toute la durée d'un appel.

Avant d'ouvrir aux clients :
- [ ] Panneau d'information RGPD près du robot : la voix et l'image servent à comprendre les demandes, rien n'est enregistré, et la tablette est effacée après chaque session.
- [ ] Utiliser un numéro dédié au robot pour l'option B (un compte WhatsApp Business si possible), jamais un numéro personnel.

## Étape 6 : base mobile sur hoverboard

On commence seulement quand le robot complet est stable sur un socle fixe. Le hoverboard n'est pas utilisé en gyropode : ses deux roues motorisées sont fixées sur un châssis avec une ou deux roulettes folles, ce qui donne une base qui ne bascule pas.

À prévoir :
- un hoverboard d'occasion, avec sa carte mère d'origine et une batterie en bon état ;
- un programmateur ST-Link V2 ;
- un adaptateur USB-série 3,3 V, pour relier la carte du hoverboard au portable ;
- un châssis en profilé alu ou contreplaqué épais, et 1 à 2 roulettes folles ;
- 3 à 4 capteurs ultrasons, plus une carte Arduino Nano (le lidar vient à l'étape 7) ;
- un deuxième bouton d'arrêt d'urgence, ou un bouton à plus de contacts.

Les étapes :
- [ ] Reprogrammer la carte avec le firmware libre [hoverboard-firmware-hack-FOC](https://github.com/EmanuelFeru/hoverboard-firmware-hack-FOC), en variante de commande par liaison série (UART). Faire un essai roues en l'air, avec une vitesse maximale basse dans la configuration.
- [ ] Construire le châssis : centre de gravité bas, robot fixé solidement, batterie et portable bien calés.
- [ ] Câbler l'arrêt d'urgence pour qu'il coupe aussi le courant des moteurs, pas seulement celui des servos.
- [ ] Ajouter les capteurs d'obstacles. Ils arrêtent les roues en local, sans attendre Claude. C'est un réflexe, comme le suivi du visage.
- [ ] Ajouter au programme Python un module `base.py`, et donner à Claude des outils avec des limites : « avancer » (distance plafonnée), « reculer », « tourner » (angle), « s'arrêter ».
- [ ] Plafonner la vitesse à celle d'une marche lente (environ 0,5 m/s). Couper les roues si le programme ne reçoit plus d'ordre pendant une seconde.
- [ ] Premiers essais dans une pièce dégagée, la main sur l'arrêt d'urgence.

## Étape 7 : navigation autonome

Le robot se repère dans le lieu et va seul vers des endroits nommés. On utilise **ROS 2 Jazzy** (la version prévue pour Ubuntu 24.04) avec **Nav2** pour les trajets et **slam_toolbox** pour dessiner la carte. Le partage des rôles reste le même : Claude décide **où** aller, et Nav2 décide **comment**, en local, plusieurs fois par seconde.

À prévoir : lidar 360°, caméra de profondeur, centrale inertielle, pare-chocs, télécommande d'arrêt sans fil (voir `materiel.md`, section 13).

- [ ] Installer ROS 2 Jazzy et Nav2 sur le portable.
- [ ] Faire remonter la vitesse des roues (capteurs à effet Hall du hoverboard, via le firmware FOC) et la centrale inertielle dans ROS 2, pour savoir de combien le robot a bougé.
- [ ] Monter le lidar au niveau de la base, la caméra de profondeur dirigée vers l'avant et le bas, et les pare-chocs avant et arrière.
- [ ] Décrire la forme du robot pour ROS 2 (fichier URDF) : taille de la base, position des capteurs.
- [ ] Piloter le robot à la main dans tout le lieu pour dessiner la carte avec slam_toolbox, puis l'enregistrer.
- [ ] Nommer les endroits sur la carte : accueil, comptoir, atelier, borne de recharge...
- [ ] Définir des zones interdites : escaliers, marches, réserve, sortie, zones de l'atelier dangereuses.
- [ ] Vitesse plafonnée à 0,5 m/s, réduite à 0,2 m/s quand quelqu'un est à moins de 1,5 m. Le robot s'arrête net si un pare-chocs est touché, si la télécommande est pressée ou si la liaison avec le portable est perdue.
- [ ] Relier ROS 2 au programme Python. Nouveaux outils pour Claude : `aller_a(lieu)`, `retour_base`, `s_arreter`, `ou_suis_je`.
- [ ] Essais : d'abord lieu fermé et vide, puis avec des personnes prévenues, puis heures calmes avec des clients.

## Étape 8 : « viens quand on t'appelle » et autonomie complète

- [ ] Remplacer le micro par le micro à plusieurs capsules (ReSpeaker), qui donne la direction d'où vient la voix.
- [ ] Mot d'appel détecté en local (par exemple « InMoov ! » ou « Robot, viens ! »), sans attendre Claude.
- [ ] À l'appel : le robot tourne la tête vers la voix, cherche la personne avec la caméra, s'approche et s'arrête à environ 1 mètre, puis dit « Bonjour, je peux vous aider ? ».
- [ ] Si personne n'est visible, aller vers la zone de la carte d'où vient la voix, sans jamais entrer dans une zone interdite.
- [ ] Mode accueil : quand un visage apparaît près de l'entrée, aller saluer, proposer de l'aide et les appels WhatsApp.
- [ ] Retour automatique à la borne de recharge quand la batterie est basse, et le soir.
- [ ] Ajouter des gestes dans `cerveau/inmoov/gestes.py` et affiner les consignes de Claude dans `cerveau/inmoov/cerveau_ia.py`.
- [ ] Idées : prendre un objet simple, accompagner un client jusqu'à un endroit (« suivez-moi jusqu'au comptoir »).

## Avant d'ouvrir le robot au public

- [ ] **Licence InMoov** : les pièces sont sous licence Creative Commons « Non Commercial ». Pour un usage avec des clients, demander l'autorisation écrite de Gaël Langevin via [inmoov.fr](https://inmoov.fr).
- [ ] **Assurance** : prévenir ton assureur qu'un robot d'environ 30 à 40 kg se déplace seul au milieu des clients, et vérifier ta responsabilité civile professionnelle.
- [ ] **RGPD** : panneau d'information, pas d'enregistrement, effacement de la tablette après chaque session, aucun souvenir sur les clients.
- [ ] **Sécurité** : arrêt d'urgence sur le robot et télécommande sans fil, toujours une personne de l'équipe à proximité au début, et jamais d'enfant seul avec le robot.
