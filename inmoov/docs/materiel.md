# Liste d'achats complète

Les prix sont des ordres de grandeur à vérifier chez ton fournisseur. Les 3 imprimantes Creality K1 Max sont déjà là.

## 1. Ordinateur portable embarqué

Le gros du calcul (langage, compréhension des images, décisions) est fait par Claude sur internet. Le portable fait tourner en local tout ce qui doit être rapide : la caméra, le suivi de visage, la voix, la liaison avec l'Arduino et la tablette, et plus tard la navigation autonome (ROS 2 et Nav2, avec le lidar et la caméra de profondeur). C'est la navigation qui fixe le niveau à viser.

| Critère | Conseillé | Pourquoi |
|---|---|---|
| Processeur | Intel Core i7 (11e génération ou plus) ou AMD Ryzen 7 | navigation, vision et voix en même temps |
| Mémoire | 16 Go minimum, 32 Go si possible | ROS 2 + caméra de profondeur + Python |
| Stockage | SSD 512 Go | cartes du lieu, journaux, enregistrements |
| Ports | 3 USB-A + 1 USB-C, plus un hub USB 3.0 alimenté | Arduino, caméra, tablette, lidar, caméra de profondeur, micro |
| Réseau | Wi-Fi 6 si possible, port Ethernet appréciable | connexion au routeur Starlink |
| Poids | 1,5 kg au plus | il est porté par le robot |
| Système | **Ubuntu 24.04 LTS** | ROS 2 (navigation) tourne sous Ubuntu ; le programme Python actuel aussi |
| Batterie | pas indispensable | branché sur secteur, puis sur la batterie de la base mobile via un convertisseur |

Un portable professionnel reconditionné de 2021 ou plus récent (type Lenovo ThinkPad T14 / T14s, Dell Latitude 5420 ou plus) coche toutes les cases pour **500 à 900 €** et supporte bien d'être fixé et transporté. Vérifier avant achat que le Wi-Fi est compatible Linux (les cartes Intel le sont).

**Où le mettre** : un portable est trop large pour le torse InMoov. Le fixer sur le dos ou sur le socle, écran fermé, avec de l'aération, et le relier par USB. Penser à régler « ne rien faire quand l'écran est rabattu » dans les options d'alimentation.

## 2. Connexion internet : Starlink

Starlink convient : la latence (quelques dizaines de millisecondes) est faible à côté du temps de réflexion de Claude (1 à 3 secondes). Le portable se connecte au Wi-Fi du routeur Starlink comme à n'importe quelle box.

- Si l'antenne est masquée (arbres, toit) la connexion peut couper quelques secondes : le robot dit alors qu'il n'arrive pas à joindre son cerveau, garde ses réflexes, et repart à la phrase suivante.
- Si le robot est loin du routeur, ajouter un répéteur Wi-Fi ou un câble Ethernet (adaptateur Ethernet Starlink + adaptateur USB-Ethernet pour le portable).

## 3. Électronique de commande

| Qté | Composant | Rôle | Prix |
|---|---|---|---|
| 1 | Arduino Mega 2560 (original ou clone) + câble USB | reçoit les ordres du portable | 15-40 € |
| 2 | Carte PCA9685 16 canaux (I2C) | signal des servos, adresses 0x40 et 0x41 | 2 × 5-10 € |
| 1 | Hub USB 3.0 alimenté, 4 ports | si le portable manque de ports | 20-30 € |

## 4. Servos (27 au total)

| Qté | Modèle | Où | Prix |
|---|---|---|---|
| 12 | Hitec HS-805BB (ou équivalent 20 kg·cm, 6 V) | omoplates, épaules, rotations et biceps (4 par bras), torse (2), rotation de la tête, cou | 12 × 30-40 € |
| 13 | MG996R (métal) | doigts (5 par main), poignets (2), mâchoire | 13 × 6-10 € |
| 2 | MG90S ou SG90 | yeux (horizontal, vertical) | 2 × 3-5 € |
| — | Rallonges servo 30 cm et 50 cm (lot de 30) | les servos des bras sont loin des cartes | 15 € |

Prévoir 2 ou 3 MG996R de rechange : ce sont ceux qu'on casse en calibrant.

## 5. Alimentation et sécurité

| Qté | Composant | Rôle | Prix |
|---|---|---|---|
| 1 | Alimentation à découpage 6 V 30 A (ou 5 V 40 A) | courant des servos | 40-80 € |
| 1 | Bouton coup de poing d'arrêt d'urgence, 2 contacts (1 NO + 1 NF) | arrêt d'urgence | 15 € |
| 1 | Relais ou contacteur 30 A, bobine 12 V ou 230 V selon montage | coupé par le bouton | 15-25 € |
| 1 | Porte-fusibles + fusibles 5 A et 10 A | un par groupe de servos | 15 € |
| 2 | Bornier de distribution | répartition V+ et GND | 15 € |
| — | Fil 1,5 mm² rouge et noir (5 m chacun), fil fin pour l'I2C | | 20 € |
| 1 | Boîtier électrique fermé | le 230 V ne doit jamais être accessible | 15 € |
| 1 | Cordon secteur avec interrupteur | | 10 € |

## 6. Vision, voix

| Qté | Composant | Rôle | Prix |
|---|---|---|---|
| 1 | Mini caméra USB 720p ou 1080p (module carte nue ou caméra endoscope ≤ 20 mm) | œil du robot | 15-30 € |
| 1 | Micro USB (de préférence omnidirectionnel, type « conférence ») | oreilles | 15-30 € |
| 1 | Haut-parleur USB ou petite enceinte alimentée en USB | voix, à placer dans la tête ou le torse | 15-25 € |

## 7. Mécanique et quincaillerie

| Composant | Prix |
|---|---|
| Fil de pêche tressé 0,8 mm (tendons des doigts) | 10 € |
| Assortiment de vis M3, M4 (longueurs 10 à 30 mm) avec écrous et rondelles | 20 € |
| Tiges filetées et vis M8, écrous M8 (épaules, torse) | 15 € |
| Roulements à billes (608ZZ et autres, voir la notice de chaque partie InMoov) | 15-25 € |
| Ressorts de traction pour les doigts | 10 € |
| Colle cyanoacrylate, colle époxy | 15 € |
| Socle / pied solide (profilé alu, bois, ou support InMoov) | 50-100 € |

## 8. Filament

| Matière | Quantité | Prix |
|---|---|---|
| PLA+ (couleur principale) | 8-10 kg | 160-200 € |
| PETG ou ASA (pièces mécaniques) | 2-3 kg | 50-70 € |
| PLA d'une 2e couleur (visage, finitions), optionnel | 1-2 kg | 20-40 € |

## 9. Outillage (si tu ne l'as pas déjà)

- Multimètre
- Fer à souder + étain (cavalier d'adresse de la PCA9685, connexions d'alimentation)
- Pince à dénuder, pince coupante, gaine thermorétractable
- Jeu de clés Allen, tournevis de précision
- Limes, cutter, forets 3 et 4 mm (ajustage des pièces imprimées)

## 10. Logiciel et services

| Élément | Prix |
|---|---|
| IDE Arduino, Python, bibliothèques | gratuits |
| Fichiers STL InMoov (inmoov.fr) | gratuits (licence CC BY-NC) |
| Clé API Claude (console.anthropic.com) | paiement à l'usage : chaque échange coûte quelques centimes au plus, à suivre dans la console |
| Starlink | abonnement existant |

## 11. Tablette et appels WhatsApp (étape 5)

| Qté | Composant | Rôle | Prix |
|---|---|---|---|
| 1 | Tablette Android 10 à 11 pouces, Android 13 ou plus récent, 4 Go de RAM minimum, bonne caméra avant (type Samsung Galaxy Tab A9+ / S6 Lite, Lenovo Tab M11) | écran, caméra et micro des appels visio, affichage du QR code | 150-300 € |
| 1 | Support de tablette à fixer sur le torse (VESA ou pince, ou pièce imprimée) | tenir la tablette à hauteur de visage | 20-40 € |
| 1 | Câble USB-C ↔ USB-A de 1,5 à 2 m, qualité données | commande de la tablette depuis le portable (ADB) et recharge | 10-15 € |
| 1 | Carte SIM ou numéro dédié (forfait à petit prix) | compte WhatsApp du robot (option B) | 2-10 €/mois |
| 1 | Panneau ou affichette d'information des clients | RGPD : ce que fait le robot avec la voix et l'image | 10-20 € |

## 12. Base mobile sur hoverboard (étape 6)

À acheter seulement quand le robot complet tient sur son socle fixe (voir `feuille-de-route.md`, étape 6).

| Qté | Composant | Rôle | Prix |
|---|---|---|---|
| 1 | Hoverboard d'occasion, roues 6,5 pouces, avec sa carte mère, sa batterie 36 V et son chargeur | moteurs, batterie, carte de commande | 50-120 € |
| 1 | Programmateur ST-Link V2 | reprogrammer la carte avec hoverboard-firmware-hack-FOC | 5-15 € |
| 1 | Adaptateur USB-série 3,3 V (CP2102 ou FTDI ; surtout pas en 5 V) | liaison portable ↔ carte du hoverboard | 5-10 € |
| 1 | Châssis : profilé alu 20×20 ou contreplaqué 18 mm, équerres, visserie | porte le robot, la batterie et le portable | 40-80 € |
| 2 | Roulette folle pivotante Ø 50-75 mm, charge 50 kg ou plus | stabilité avant/arrière | 2 × 8-15 € |
| 4 | Capteur à ultrasons HC-SR04 | détection des obstacles proches, arrêt réflexe | 10 € |
| 1 | Arduino Nano | lit les capteurs et arrête les roues en local | 5-20 € |
| 1 | Bouton coup de poing d'arrêt d'urgence + relais ou interrupteur de puissance 36 V / 30 A | coupe le courant des moteurs | 25-40 € |
| 1 | Porte-fusible + fusible 30 A, connecteurs XT60 | protection de la batterie | 10-15 € |

La batterie lithium d'un hoverboard est puissante : n'en prendre que si elle est intacte (pas gonflée, pas cabossée), la recharger avec son chargeur d'origine, sous surveillance, et la garder bien protégée dans le châssis.

## 13. Navigation autonome et « viens quand on t'appelle » (étapes 7 et 8)

| Qté | Composant | Rôle | Prix |
|---|---|---|---|
| 1 | Lidar 360° (RPLIDAR C1 ou A1, ou LDROBOT LD19) | dessiner la carte, se repérer, voir les obstacles | 80-120 € |
| 1 | Caméra de profondeur (Luxonis OAK-D Lite ou Intel RealSense D435) | voir les tables, chaises et objets que le lidar ne voit pas | 150-300 € |
| 1 | Micro à plusieurs capsules (ReSpeaker USB 4 ou 6 micros) | savoir d'où vient la voix qui appelle le robot ; remplace le micro simple | 40-80 € |
| 1 | Centrale inertielle (BNO085) | mesurer précisément les rotations de la base | 20-30 € |
| 2 | Pare-chocs avec micro-rupteurs (avant et arrière) | arrêt immédiat au moindre contact | 20 € |
| 1 | Télécommande d'arrêt d'urgence sans fil (récepteur à relais) | arrêter le robot à distance | 30-60 € |
| 1 | Convertisseur 36 V → 20 V (USB-C PD ou alimentation du portable) | alimenter le portable depuis la batterie de la base | 30-50 € |
| 1 | Socle de recharge (optionnel) | le robot retourne se recharger seul | 50-100 € |

## Budget total indicatif

| Poste | Estimation |
|---|---|
| Ordinateur portable reconditionné (Ubuntu, Core i7 / Ryzen 7) | 500-900 € |
| Servos | 550-650 € |
| Électronique de commande | 40-90 € |
| Alimentation et sécurité | 160-210 € |
| Vision et voix | 45-85 € |
| Mécanique, quincaillerie, socle | 150-200 € |
| Filament | 230-310 € |
| **Total robot fixe (outillage non compris)** | **environ 1 700 à 2 450 €** |
| Tablette et appels (étape 5) | 190-375 € (+ forfait SIM mensuel) |
| Base mobile hoverboard (étape 6) | 165-340 € |
| Navigation autonome (étapes 7 et 8) | 370-760 € |
| **Total robot complet et autonome** | **environ 2 400 à 3 900 €** |

## Par où commencer les achats

Pas besoin de tout acheter d'un coup. Pour l'étape 1 (main + avant-bras droits) :
1. Arduino Mega, 1 carte PCA9685
2. 6 servos MG996R (+ 2 de rechange)
3. Alimentation 6 V, bouton d'arrêt d'urgence, relais, bornier, fusibles
4. 2 kg de PLA+, fil de pêche tressé, vis M3
5. Le portable
