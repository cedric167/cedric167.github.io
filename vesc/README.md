# VESC Web Tool

Réplique web de [VESC Tool](https://github.com/vedderb/vesc_tool) pour configurer et surveiller
un contrôleur VESC depuis le navigateur, par Bluetooth (Web Bluetooth) ou USB (Web Serial).

En ligne : https://cedric167.github.io/vesc/

## Fonctions

| Page | Contenu |
|---|---|
| Connexion | Bluetooth (service UART Nordic), USB, mode démo ; infos firmware/matériel ; scan du bus CAN et choix de la cible ; redémarrage |
| Temps réel | Tension, courants, puissance, duty, ERPM, températures, Ah/Wh, tachymètre, défauts ; graphiques ; enregistrement CSV |
| Moteur / App | Tous les paramètres `mcconf` / `appconf`, groupés comme dans VESC Tool, avec aide ; lecture, valeurs par défaut, écriture vérifiée ; import/export XML compatible VESC Tool |
| Détection | Assistant de détection FOC (préréglages de moteurs de VESC Tool, détection CAN) ; mesure R/L |
| Contrôle | Duty, courant, frein, ERPM, frein à main, en mode « maintenir pour activer » |
| Entrées | Valeurs PPM, ADC et IMU décodées |
| Terminal | Commandes du terminal VESC |
| Firmware | Envoi d'un firmware `.bin` non compressé (local ou tout le bus CAN) |

Les définitions de paramètres de tous les firmwares de 3.55 à 7.01 sont incluses (`config/`).
La bonne version est choisie grâce à la signature envoyée par le VESC, identique à celle du firmware
(`MCCONF_SIGNATURE` / `APPCONF_SIGNATURE`).

## Navigateurs

Chrome ou Edge sur Android, Windows, macOS, Linux. Safari (iPhone/iPad) ne gère pas Web Bluetooth :
utiliser l'application Bluefy. La page doit être servie en HTTPS (c'est le cas sur GitHub Pages).

## Pas encore repris de VESC Tool

- firmwares compressés (heatshrink) et envoi LZO, bootloader ;
- interfaces QML personnalisées, packages, scripts LispBM ;
- BMS, journaux sur carte SD, configurations personnalisées (`custom config`) ;
- étapes batterie / roue de l'assistant de configuration.

## Développement

Aucune étape de compilation : HTML, CSS et modules JavaScript.

```sh
python3 -m http.server 8000          # puis http://localhost:8000/vesc/
node vesc/tests/protocol.test.mjs    # tests du protocole et des 50 définitions
```

Régénérer les définitions depuis un clone de VESC Tool :

```sh
python3 vesc/tools/convert_config.py ../vesc_tool/res/config vesc/config
```

## Licence

GPL-3.0 (voir `LICENSE`), comme VESC Tool dont ce code reprend le protocole et les définitions de paramètres.
