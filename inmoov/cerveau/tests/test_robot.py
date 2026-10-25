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
