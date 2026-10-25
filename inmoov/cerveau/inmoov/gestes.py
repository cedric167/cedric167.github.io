"""Gestes préenregistrés : des suites de poses jouées par le corps.

Chaque geste est une liste d'étapes (cibles, durée en secondes). Les angles
passent par les butées de config.yaml, donc un geste trop ample est
simplement raccourci, jamais forcé.
"""

import time

MAIN_OUVERTE = {"pouce": 0, "index": 0, "majeur": 0, "annulaire": 0, "auriculaire": 0}
MAIN_FERMEE = {"pouce": 150, "index": 170, "majeur": 170, "annulaire": 170, "auriculaire": 170}


def main(cote: str, doigts: dict) -> dict:
    return {f"{cote}_{doigt}": angle for doigt, angle in doigts.items()}


GESTES = {
    "saluer": [
        ({"droit_epaule": 140, "droit_biceps": 70, "droit_rotation": 90, **main("droit", MAIN_OUVERTE)}, 1.5),
        ({"droit_poignet": 50}, 0.4),
        ({"droit_poignet": 130}, 0.4),
        ({"droit_poignet": 50}, 0.4),
        ({"droit_poignet": 90}, 0.4),
        ({"droit_epaule": 30, "droit_biceps": 5}, 1.5),
    ],
    "tendre_la_main": [
        ({"droit_epaule": 70, "droit_biceps": 40, "droit_rotation": 90, **main("droit", MAIN_OUVERTE)}, 1.5),
    ],
    "pointer_devant": [
        ({"droit_epaule": 100, "droit_biceps": 10, **main("droit", MAIN_FERMEE), "droit_index": 0}, 1.5),
    ],
    "ouvrir_main_droite": [(main("droit", MAIN_OUVERTE), 0.8)],
    "fermer_main_droite": [(main("droit", MAIN_FERMEE), 0.8)],
    "ouvrir_main_gauche": [(main("gauche", MAIN_OUVERTE), 0.8)],
    "fermer_main_gauche": [(main("gauche", MAIN_FERMEE), 0.8)],
    "hocher_oui": [
        ({"cou": 110}, 0.3), ({"cou": 75}, 0.3), ({"cou": 110}, 0.3), ({"cou": 90}, 0.3),
    ],
    "secouer_non": [
        ({"tete_rotation": 70}, 0.3), ({"tete_rotation": 110}, 0.3),
        ({"tete_rotation": 70}, 0.3), ({"tete_rotation": 90}, 0.3),
    ],
    "reflechir": [
        ({"cou": 105, "tete_rotation": 75, "yeux_vertical": 110}, 1.0),
    ],
    "position_repos": [],  # traité à part : chaque articulation revient à sa valeur "repos"
}


def jouer(corps, nom: str):
    if nom not in GESTES:
        raise KeyError(f"Geste inconnu : {nom}")
    if nom == "position_repos":
        corps.repos()
        return
    for cibles, duree in GESTES[nom]:
        # Vitesse calculée pour que l'étape la plus ample tienne dans la durée prévue.
        ecart = max(abs(angle - corps.positions[art]) for art, angle in cibles.items())
        corps.bouger_plusieurs(cibles, vitesse=max(20, int(ecart / duree)))
        time.sleep(duree)
