# Robot InMoov piloté par Claude

Construction d'un robot humanoïde [InMoov](https://inmoov.fr) complet (tête, yeux, mains, bras, torse), avec un ordinateur portable embarqué et Claude comme cerveau : il voit par la caméra de son œil, écoute, parle, se souvient et commande lui-même ses mouvements.

Plus tard (voir la feuille de route) : une tablette Android sur le torse pour que les clients passent des appels WhatsApp en visio ou en audio, une base mobile sur hoverboard, puis la navigation autonome : le robot vient seul quand on l'appelle.

## Comment ça marche

```
        ┌──────────────────────────────────────┐
        │  CLAUDE (API, sur internet)          │
        │  vision, dialogue, décisions         │
        └─────────────────▲────────────────────┘
                          │ Wi-Fi
┌─────────────────────────┴──────────────────────────────┐
│  ORDINATEUR PORTABLE (dos du robot ou socle)           │
│  cerveau/main.py                                       │
│   - corps.py    : articulations, butées, liaison USB   │
│   - vision.py   : caméra de l'œil + suivi de visage    │
│   - voix.py     : micro, synthèse vocale, mâchoire     │
│   - cerveau_ia.py : boucle avec Claude et ses outils   │
└─────────────────────────▲──────────────────────────────┘
                          │ USB
┌─────────────────────────┴──────────────────────────────┐
│  ARDUINO MEGA  firmware/inmoov_servos                  │
│  2 cartes PCA9685 (I2C) -> 27 servos                   │
│  bouton d'arrêt d'urgence                              │
└────────────────────────────────────────────────────────┘
```

Deux niveaux de décision :
- **Réflexes en local** (sans internet) : suivi du visage 15 fois par seconde, mouvements lissés par l'Arduino, butées, arrêt d'urgence.
- **Réflexion par Claude** (1 à 3 secondes par décision) : comprendre ce qu'on lui dit, regarder une photo, choisir un geste, répondre, retenir un souvenir.

Claude ne commande jamais un servo directement : il appelle des outils (`bouger_articulations`, `faire_geste`, `prendre_photo`, `suivi_visage`, `etat_du_corps`, `noter_souvenir`), et le programme vérifie chaque angle contre les butées de `config.yaml`.

## Contenu du dossier

| Chemin | Rôle |
|---|---|
| [`docs/feuille-de-route.md`](docs/feuille-de-route.md) | Les étapes de construction, dans l'ordre |
| [`docs/materiel.md`](docs/materiel.md) | Liste d'achats complète : ordinateur, Starlink, budget |
| [`docs/impression.md`](docs/impression.md) | Plan d'impression sur les 3 Creality K1 Max |
| [`docs/cablage.md`](docs/cablage.md) | Alimentation, cartes, numéro de canal de chaque servo |
| [`docs/securite.md`](docs/securite.md) | Règles de sécurité (à lire avant le premier mouvement) |
| [`firmware/inmoov_servos/`](firmware/inmoov_servos/) | Programme de l'Arduino |
| [`cerveau/`](cerveau/) | Programme Python de l'ordinateur portable |

## Démarrage rapide (sans robot)

On peut tout tester avant d'avoir imprimé la moindre pièce :

```bash
cd inmoov/cerveau
python -m venv .venv
source .venv/bin/activate          # Windows : .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # puis mets ta clé API dans .env
python -m pytest                   # tests sans matériel
python main.py --simulation --texte
```

En mode `--simulation`, les mouvements sont calculés sans Arduino ; en mode `--texte`, on parle au robot au clavier. La webcam du portable sert d'œil si elle existe (`--sans-camera` pour la désactiver).

Avec le robot branché : `python main.py` (micro et haut-parleur), ou `python main.py --texte`.

## Ce qu'il faut savoir

- **Internet obligatoire** pour la réflexion : Claude tourne sur les serveurs d'Anthropic. Sans connexion, le robot garde ses réflexes mais ne parle plus.
- **Coût à l'usage** de l'API Claude : chaque échange est facturé (texte et photos). Le réglage `effort: low` de `config.yaml` garde les réponses rapides et économes.
- **Clé API** : à créer sur [console.anthropic.com](https://console.anthropic.com). Elle va dans `cerveau/.env`, qui n'est jamais envoyé sur GitHub. Ce dépôt est public (c'est le site cedric167.github.io) : ne colle jamais la clé ailleurs.
- **Licence InMoov** : les pièces de Gaël Langevin sont sous licence Creative Commons BY-NC, donc pas d'usage commercial.
