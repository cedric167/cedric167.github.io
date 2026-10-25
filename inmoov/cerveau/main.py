"""Point d'entrée : lance le robot InMoov piloté par Claude.

Exemples :
    python main.py --simulation --texte   # sans robot, au clavier (pour tester)
    python main.py --texte                # robot branché, au clavier
    python main.py                        # robot branché, micro et haut-parleur
"""

import argparse
from pathlib import Path

import yaml
from dotenv import load_dotenv

from inmoov.cerveau_ia import Cerveau
from inmoov.corps import Corps

DOSSIER = Path(__file__).resolve().parent
MOTS_DE_FIN = {"au revoir", "stop", "arrête-toi", "éteins-toi"}


def main():
    parser = argparse.ArgumentParser(description="Robot InMoov piloté par Claude")
    parser.add_argument("--simulation", action="store_true", help="sans Arduino : les mouvements sont simulés")
    parser.add_argument("--texte", action="store_true", help="clavier et écran au lieu du micro et du haut-parleur")
    parser.add_argument("--sans-camera", action="store_true", help="ne pas ouvrir la caméra")
    parser.add_argument("--config", default=DOSSIER / "config.yaml")
    args = parser.parse_args()

    load_dotenv(DOSSIER / ".env")
    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))

    corps = Corps(config, simulation=args.simulation)
    vision = None
    if not args.sans_camera:
        from inmoov.vision import Vision
        vision = Vision(config, corps)
        if not vision.disponible:
            print("Caméra introuvable : le robot fonctionnera sans la vue.")
    from inmoov.voix import Voix
    voix = Voix(config, corps, mode_texte=args.texte)
    cerveau = Cerveau(config, corps, vision, voix)

    print("Robot prêt. Dis « au revoir » pour l'arrêter.")
    corps.repos()
    try:
        while True:
            phrase = voix.ecouter()
            if not phrase:
                continue
            if phrase.lower().strip(" .!") in MOTS_DE_FIN:
                voix.parler("Au revoir !")
                break
            cerveau.repondre(phrase)
    except KeyboardInterrupt:
        pass
    finally:
        if vision:
            vision.suivi_actif = False
        try:
            corps.repos()
        except Exception:
            pass
        if vision:
            vision.fermer()
        corps.fermer()


if __name__ == "__main__":
    main()
