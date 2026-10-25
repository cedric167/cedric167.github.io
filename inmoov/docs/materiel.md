# Liste d'achats complète

Les prix sont des ordres de grandeur à vérifier chez ton fournisseur. Les 3 imprimantes Creality K1 Max sont déjà là.

## 1. Ordinateur portable embarqué

Le gros du calcul (vision, langage, décisions) est fait par Claude sur internet. Le portable fait tourner la caméra, le suivi de visage, la voix et la liaison avec l'Arduino : pas besoin d'une machine de jeu.

| Critère | Minimum conseillé | Pourquoi |
|---|---|---|
| Processeur | Intel Core i5 (8e génération ou plus) ou AMD Ryzen 5 | suivi de visage en temps réel |
| Mémoire | 16 Go | caméra + voix + Python sans ralentir |
| Stockage | SSD 256 Go ou plus | démarrage rapide, enregistrements |
| Ports | 3 USB-A (ou USB-C + hub alimenté) | Arduino, caméra, micro/haut-parleur |
| Réseau | Wi-Fi 5 ou mieux | connexion au routeur Starlink |
| Poids | 1,5 kg au plus | il est porté par le robot |
| Système | Windows 10/11 ou Linux (Ubuntu) | Python 3.10+ |
| Batterie | pas indispensable | il sera branché sur secteur |

Un portable professionnel reconditionné (type Lenovo ThinkPad série T ou E, Dell Latitude) coche toutes les cases pour **400 à 700 €** et supporte bien d'être fixé et transporté.

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

## Budget total indicatif

| Poste | Estimation |
|---|---|
| Ordinateur portable reconditionné | 400-700 € |
| Servos | 550-650 € |
| Électronique de commande | 40-90 € |
| Alimentation et sécurité | 160-210 € |
| Vision et voix | 45-85 € |
| Mécanique, quincaillerie, socle | 150-200 € |
| Filament | 230-310 € |
| **Total (outillage non compris)** | **environ 1 600 à 2 250 €** |

## Par où commencer les achats

Pas besoin de tout acheter d'un coup. Pour l'étape 1 (main + avant-bras droits) :
1. Arduino Mega, 1 carte PCA9685
2. 6 servos MG996R (+ 2 de rechange)
3. Alimentation 6 V, bouton d'arrêt d'urgence, relais, bornier, fusibles
4. 2 kg de PLA+, fil de pêche tressé, vis M3
5. Le portable
