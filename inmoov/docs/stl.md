# Pièces à imprimer (STL)

Les fichiers STL officiels sont gratuits sur [inmoov.fr](https://inmoov.fr). Ils sont rangés partie par partie dans la galerie du site, et chaque partie a une page de montage. Ils sont sous licence Creative Commons BY-NC (pas d'usage commercial sans l'accord de Gaël Langevin) : on ne les copie pas dans ce dépôt, on les télécharge sur le site.

> **À compléter** : la liste exacte des fichiers (nom de chaque STL et quantité) n'a pas encore pu être relevée, car inmoov.fr n'était pas accessible depuis l'environnement où ce document a été écrit. Ce qui suit donne les parties et l'ordre d'impression. Le détail fichier par fichier est sur la page de chaque partie.

## Règles d'impression communes (recommandations du site InMoov)

- **Imprimer d'abord le CALIBRATOR** (pièce de calibration fournie dans la galerie) pour vérifier que les pièces s'emboîtent. Si c'est trop serré ou trop lâche, ajuster l'expansion horizontale (« horizontal expansion ») dans le trancheur avant d'imprimer le reste.
- Remplissage 30 %, parois de 2,5 mm environ.
- Pas de radeau ni de supports, sauf quand la page de la pièce l'indique (bouts de doigts, capots, certaines pièces de l'avant-bras).
- Hauteur de couche de 0,25 mm au maximum (0,12 à 0,2 mm pour les doigts).
- Les réglages propres aux K1 Max (matières, vitesse, répartition entre les 3 imprimantes) sont dans [`impression.md`](impression.md).

## Liste par partie, dans l'ordre de la feuille de route

Le côté gauche est le miroir du côté droit : le site fournit des fichiers gauches pour la main, l'avant-bras, le biceps et l'épaule. Imprimer le côté droit en premier, le monter, le tester, puis faire le gauche.

### 0. Calibration

- [ ] CALIBRATOR (galerie inmoov.fr)

### Étape 1 : main et avant-bras droits

Page : [Hand and Forarm](https://inmoov.fr/hand-and-forarm/), ou la version récente [Hand i2](https://inmoov.fr/hand-i2/), que l'auteur recommande à la place de la main d'origine.

- [ ] Main droite : 5 doigts (phalanges et bouts de doigts), paume, capots. Une seule fois chaque pièce pour une main.
- [ ] Poignet : pièces du poignet et engrenages de rotation.
- [ ] Avant-bras droit : coques de l'avant-bras (pièces « robpart ») et support des servos des doigts (servo bed).
- [ ] Pièces de tension des fils des doigts.

### Étape 2 : tête, cou, mâchoire, yeux

Pages : [Neck and jaw](https://inmoov.fr/build-yours/neck-and-jaw/), [Head](https://inmoov.fr/head-3/). L'auteur propose aussi une tête plus avancée, i2Head, qui demande du moulage en silicone : à garder pour plus tard.

- [ ] Mécanisme du cou (rotation et inclinaison de la tête)
- [ ] Mécanisme de la mâchoire
- [ ] Mécanisme des yeux (support de la caméra dans un œil)
- [ ] Crâne (pièces du crâne et de l'arrière de la tête)
- [ ] Visage (pièces du visage, à imprimer avec soin, c'est ce qu'on voit le plus)

Monter les mécanismes intérieurs avant de fermer avec la coque.

### Étape 3 : bras droit

Pages : [Bicep](https://inmoov.fr/bicep/), [Shoulder and torso](https://inmoov.fr/shoulder-and-torso/).

- [ ] Biceps droit : coques, engrenages, support du servo du coude
- [ ] Rotation du bras (entre l'épaule et le biceps)
- [ ] Épaule droite : pièces de clavicule avant et arrière, supports de potentiomètre, engrenages de l'épaule
- [ ] Omoplate droite

### Étape 4 : torse et bras gauche

Page : [Shoulder and torso](https://inmoov.fr/shoulder-and-torso/), [Top stomach](https://inmoov.fr/top-stomach/).

- [ ] Poitrine (chest)
- [ ] Dos (back)
- [ ] Ventre haut (top stomach) et ventre milieu (mid stomach), avec leurs mécanismes de rotation
- [ ] Supports « Kinect » au centre du torse : à l'origine prévus pour une caméra Kinect, ils peuvent servir à fixer la caméra de profondeur de l'étape 7, ou la tablette de l'étape 5 avec un support adapté
- [ ] Côté gauche complet : main, avant-bras, biceps, rotation, épaule, omoplate (versions gauches des fichiers des étapes 1 et 3)

### Pièces à dessiner pour ce projet (pas sur inmoov.fr)

- [ ] Support de tablette sur le torse (étape 5)
- [ ] Supports du lidar, de la caméra de profondeur et des capteurs à ultrasons sur la base mobile (étapes 6 et 7)
- [ ] Boîtier de l'Arduino et des cartes PCA9685
- [ ] Fixation du portable sur le dos ou sur le socle

## Sources

- [Liste des pièces originales et licence](https://inmoov.fr/?p=12)
- [Hand and Forarm](https://inmoov.fr/hand-and-forarm/) · [Hand i2](https://inmoov.fr/hand-i2/) · [InMoov New Hand 2020](https://inmoov.fr/inmoov-hand/)
- [Neck and jaw](https://inmoov.fr/build-yours/neck-and-jaw/) · [Head](https://inmoov.fr/head-3/)
- [Bicep](https://inmoov.fr/bicep/) · [Shoulder and torso](https://inmoov.fr/shoulder-and-torso/) · [Top stomach](https://inmoov.fr/top-stomach/)
