# Câblage

## Schéma général

```
  Secteur 230 V
       │
 ┌─────┴──────────┐      ┌──────────────────────────┐
 │ Alimentation   │ 6 V  │ Relais / contacteur 30 A │
 │ 6 V 30 A       ├──────┤ (coupé par le bouton     ├──► V+ servos (bornier)
 └─────┬──────────┘      │  d'arrêt d'urgence)      │
       │ GND             └──────────────────────────┘
       └─────────────────────────────────────────────► GND servos (bornier)
                                                            │
 Portable ──USB── Arduino Mega                               │
                    5V  ──► VCC  PCA9685 0x40 ──┬── VCC PCA9685 0x41
                    GND ──► GND  (masse commune avec les servos !)
                    SDA (20) ──► SDA ───────────┴── SDA
                    SCL (21) ──► SCL ───────────┴── SCL
                    D2  ──► 2e contact du bouton d'arrêt ──► GND
```

Points importants :
- **Le courant des servos ne passe pas par l'Arduino.** Les servos sont alimentés depuis le bornier ; la borne V+ des PCA9685 ne doit pas porter tout le courant (les gros servos des épaules tirent 2 à 3 A chacun en effort). Pour les épaules, brancher le + et le − du servo directement sur le bornier et seulement le fil de signal sur la PCA9685.
- **Masse commune** : le GND de l'alimentation, des PCA9685 et de l'Arduino doivent être reliés, sinon les servos tremblent.
- **Adresse 0x41** : sur la deuxième carte PCA9685, souder le cavalier A0.
- **Fusibles** : un fusible par groupe (tête, bras droit, bras gauche, torse).
- **Arrêt d'urgence** : le bouton a deux contacts. Le premier coupe le relais, donc l'alimentation des servos. Le second relie D2 à la masse ; quand on l'enfonce, D2 passe à HIGH et le firmware refuse tout mouvement. Les deux ensemble : les servos n'ont plus de courant, et le programme le sait.

## Canaux des servos

Les numéros correspondent au `canal` dans `cerveau/config.yaml`.

### Carte 0x40 (canaux 0 à 15)

| Canal | Articulation | Canal | Articulation |
|---|---|---|---|
| 0 | tete_rotation | 8 | droit_biceps |
| 1 | cou | 9 | droit_poignet |
| 2 | machoire | 10 | droit_pouce |
| 3 | yeux_horizontal | 11 | droit_index |
| 4 | yeux_vertical | 12 | droit_majeur |
| 5 | droit_omoplate | 13 | droit_annulaire |
| 6 | droit_epaule | 14 | droit_auriculaire |
| 7 | droit_rotation | 15 | (libre) |

### Carte 0x41 (canaux 16 à 31, prise 0 à 15 sur la carte)

| Canal | Prise | Articulation | Canal | Prise | Articulation |
|---|---|---|---|---|---|
| 16 | 0 | gauche_omoplate | 22 | 6 | gauche_index |
| 17 | 1 | gauche_epaule | 23 | 7 | gauche_majeur |
| 18 | 2 | gauche_rotation | 24 | 8 | gauche_annulaire |
| 19 | 3 | gauche_biceps | 25 | 9 | gauche_auriculaire |
| 20 | 4 | gauche_poignet | 26 | 10 | torse_haut |
| 21 | 5 | gauche_pouce | 27 | 11 | torse_milieu |

## Téléverser le firmware

1. Installer l'IDE Arduino.
2. Gestionnaire de bibliothèques : installer **Adafruit PWM Servo Driver Library**.
3. Ouvrir `firmware/inmoov_servos/inmoov_servos.ino`, carte « Arduino Mega or Mega 2560 », téléverser.
4. Moniteur série à 115200 bauds, fin de ligne « Nouvelle ligne » : taper `P`, la réponse doit être `OK`.
