"""Tests sans matériel ni appel à l'API : python -m pytest tests"""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from inmoov import cerveau_ia, gestes
from inmoov.corps import Corps

CONFIG = yaml.safe_load((Path(__file__).resolve().parent.parent / "config.yaml").read_text(encoding="utf-8"))


@pytest.fixture
def corps():
    return Corps(CONFIG, simulation=True)


def test_butees_respectees(corps):
    assert corps.bouger("tete_rotation", 500) == CONFIG["articulations"]["tete_rotation"]["max"]
    assert corps.bouger("tete_rotation", -20) == CONFIG["articulations"]["tete_rotation"]["min"]


def test_articulation_inconnue(corps):
    with pytest.raises(KeyError):
        corps.bouger("queue", 90)


def test_canaux_uniques():
    canaux = [a["canal"] for a in CONFIG["articulations"].values()]
    assert len(canaux) == len(set(canaux))
    assert all(0 <= c < 32 for c in canaux)


def test_repos_dans_les_butees():
    for nom, a in CONFIG["articulations"].items():
        assert a["min"] <= a["repos"] <= a["max"], nom


def test_gestes_utilisent_des_articulations_existantes():
    for nom, etapes in gestes.GESTES.items():
        for cibles, duree in etapes:
            assert set(cibles) <= set(CONFIG["articulations"]), nom
            assert duree > 0


def test_gestes_jouables(corps, monkeypatch):
    monkeypatch.setattr(gestes.time, "sleep", lambda _: None)
    for nom in gestes.GESTES:
        gestes.jouer(corps, nom)


class FausseVoix:
    def __init__(self):
        self.dit = []

    def parler(self, texte):
        self.dit.append(texte)


def bloc_outil(nom, entree, identifiant="outil_1"):
    return SimpleNamespace(type="tool_use", name=nom, input=entree, id=identifiant)


@pytest.fixture
def cerveau(corps, monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    monkeypatch.setattr(cerveau_ia, "FICHIER_MEMOIRE", tmp_path / "memoire.json")
    return cerveau_ia.Cerveau(CONFIG, corps, vision=None, voix=FausseVoix())


def test_outil_bouger(cerveau):
    resultat = cerveau._executer(bloc_outil(
        "bouger_articulations",
        {"mouvements": [{"articulation": "cou", "angle": 999}], "vitesse": 30},
    ))
    assert "is_error" not in resultat
    assert json.loads(resultat["content"])["angles_atteints"]["cou"] == CONFIG["articulations"]["cou"]["max"]


def test_outil_arret_urgence(cerveau, monkeypatch):
    monkeypatch.setattr(cerveau.corps, "_envoyer", lambda commande: "ESTOP")
    resultat = cerveau._executer(bloc_outil("faire_geste", {"geste": "saluer"}))
    assert resultat["is_error"] is True
    assert "urgence" in resultat["content"]


def test_outil_photo_sans_camera(cerveau):
    assert cerveau._executer(bloc_outil("prendre_photo", {}))["content"] == "Aucune caméra disponible."


def test_souvenirs(cerveau):
    cerveau._executer(bloc_outil("noter_souvenir", {"souvenir": "Cédric aime les foils"}))
    cerveau.nouvelle_conversation()
    assert "Cédric aime les foils" in cerveau.systeme


def test_boucle_complete(cerveau, monkeypatch):
    """Claude demande un geste, reçoit le résultat, puis répond."""
    reponses = iter([
        SimpleNamespace(stop_reason="tool_use", content=[
            SimpleNamespace(type="text", text="Bonjour !"),
            bloc_outil("faire_geste", {"geste": "hocher_oui"}),
        ]),
        SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text="Ravi de te voir.")]),
    ])
    monkeypatch.setattr(gestes.time, "sleep", lambda _: None)
    monkeypatch.setattr(cerveau, "_appeler_claude", lambda: next(reponses))
    cerveau.repondre("Salut robot")
    assert cerveau.voix.dit == ["Bonjour !", "Ravi de te voir."]
    assert [m["role"] for m in cerveau.messages] == ["user", "assistant", "user", "assistant"]
    assert cerveau.messages[2]["content"][0]["type"] == "tool_result"


def test_schemas_outils_stricts(cerveau):
    for outil in cerveau.outils:
        assert outil["strict"] is True
        assert outil["input_schema"]["additionalProperties"] is False


class FausseCamera:
    def __init__(self, *_):
        pass

    def set(self, *_):
        pass

    def isOpened(self):
        return False

    def release(self):
        pass


@pytest.fixture
def vision(corps, monkeypatch):
    from inmoov import vision as module_vision
    monkeypatch.setattr(module_vision.cv2, "VideoCapture", FausseCamera)
    return module_vision.Vision(CONFIG, corps)


def test_regard_suit_un_visage(vision, corps):
    """Visage à 20° sur la droite : les yeux réagissent, puis la tête les rattrape."""
    art = corps.articulations
    visage_h, visage_v = -20, 10  # en degrés : droite négative, haut positif
    demi_champ = 30               # demi-angle de vue de la caméra

    def ecarts():
        regard_h = (corps.positions["yeux_horizontal"] - art["yeux_horizontal"].repos
                    + corps.positions["tete_rotation"] - art["tete_rotation"].repos)
        regard_v = (corps.positions["yeux_vertical"] - art["yeux_vertical"].repos
                    + corps.positions["cou"] - art["cou"].repos)
        # Dans l'image, x va vers la droite du robot et y vers le bas.
        return (max(-1, min(1, (regard_h - visage_h) / demi_champ)),
                max(-1, min(1, (regard_v - visage_v) / demi_champ)))

    vision.suivi_actif = True
    vision.suivre(*ecarts())
    assert corps.positions["yeux_horizontal"] < art["yeux_horizontal"].repos  # les yeux partent à droite
    assert corps.positions["yeux_vertical"] > art["yeux_vertical"].repos      # et vers le haut

    for _ in range(300):
        vision.suivre(*ecarts())
    ecart_x, ecart_y = ecarts()
    assert abs(ecart_x) <= CONFIG["suivi_visage"]["zone_morte"]
    assert abs(ecart_y) <= CONFIG["suivi_visage"]["zone_morte"]
    # La tête a fait l'essentiel du chemin, les yeux sont revenus près du milieu.
    assert corps.positions["tete_rotation"] < art["tete_rotation"].repos - 10
    assert corps.positions["cou"] > art["cou"].repos + 3
    tolerance = CONFIG["suivi_visage"]["tolerance_yeux"] + 3
    assert abs(corps.positions["yeux_horizontal"] - art["yeux_horizontal"].repos) <= tolerance
    assert abs(corps.positions["yeux_vertical"] - art["yeux_vertical"].repos) <= tolerance


def test_regard_visage_centre_ne_bouge_pas(vision, corps):
    avant = dict(corps.positions)
    vision.suivre(0.02, -0.03)
    assert corps.positions == avant


def test_regard_arret_urgence_coupe_le_suivi(vision, corps, monkeypatch):
    monkeypatch.setattr(corps, "_envoyer", lambda commande: "ESTOP")
    vision.suivi_actif = True
    vision.suivre(0.5, 0.5)
    assert vision.suivi_actif is False


def test_outil_regarder(cerveau):
    art = cerveau.corps.articulations
    resultat = cerveau._executer(bloc_outil("regarder", {"horizontal": 1, "vertical": -1}))
    angles = json.loads(resultat["content"])["angles_atteints"]
    assert angles["tete_rotation"] == art["tete_rotation"].min  # tout à droite
    assert angles["cou"] == art["cou"].min                      # en bas
    assert angles["yeux_horizontal"] == art["yeux_horizontal"].repos
