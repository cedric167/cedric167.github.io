"""Le corps du robot : articulations, butées et liaison série avec l'Arduino.

Toute commande de mouvement passe par ici, qu'elle vienne de Claude, du suivi
de visage ou d'un geste préenregistré. C'est le seul endroit qui parle aux
servos, donc le seul endroit où les butées sont vérifiées.
"""

import threading
import time
from dataclasses import dataclass

try:
    import serial
    import serial.tools.list_ports
except ImportError:  # pyserial absent : seul le mode simulation fonctionne
    serial = None


class ArretUrgence(Exception):
    """Le bouton d'arrêt d'urgence est enfoncé : aucun mouvement possible."""


@dataclass
class Articulation:
    nom: str
    canal: int
    min: int
    max: int
    repos: int
    inverse: bool = False

    def borner(self, angle: float) -> int:
        return int(round(max(self.min, min(self.max, angle))))

    def angle_servo(self, angle: int) -> int:
        """Angle réellement envoyé au servo (tient compte d'un montage inversé)."""
        return 180 - angle if self.inverse else angle


class Corps:
    def __init__(self, config: dict, simulation: bool = False):
        self.articulations = {
            nom: Articulation(nom=nom, **params)
            for nom, params in config["articulations"].items()
        }
        self.positions = {nom: a.repos for nom, a in self.articulations.items()}
        self.simulation = simulation
        self.arret_urgence = False
        self._verrou = threading.Lock()
        self._serie = None
        if not simulation:
            self._connecter(config["materiel"])

    # --- Liaison série ---------------------------------------------------

    def _connecter(self, materiel: dict):
        if serial is None:
            raise RuntimeError("pyserial n'est pas installé (pip install pyserial)")
        port = materiel.get("port_serie", "auto")
        if port == "auto":
            port = self._trouver_arduino()
        self._serie = serial.Serial(port, materiel.get("vitesse_serie", 115200), timeout=1)
        time.sleep(2)  # l'Arduino redémarre à l'ouverture du port
        self._serie.reset_input_buffer()
        if self._envoyer("P") not in ("OK", "ESTOP"):
            raise RuntimeError(f"L'Arduino ne répond pas sur {port}")

    @staticmethod
    def _trouver_arduino() -> str:
        for port in serial.tools.list_ports.comports():
            description = f"{port.description} {port.manufacturer or ''}".lower()
            if "arduino" in description or "ch340" in description or "usb serial" in description:
                return port.device
        raise RuntimeError("Aucun Arduino détecté : branche-le ou indique port_serie dans config.yaml")

    def _envoyer(self, commande: str) -> str:
        """Envoie une ligne à l'Arduino et renvoie sa réponse ("OK", "ESTOP", "ERR ...")."""
        if self.simulation:
            return "OK"
        with self._verrou:
            self._serie.write((commande + "\n").encode("ascii"))
            reponse = self._serie.readline().decode("ascii", errors="replace").strip()
        if reponse == "ESTOP":
            self.arret_urgence = True
        elif reponse == "OK":
            self.arret_urgence = False
        return reponse

    # --- Mouvements ------------------------------------------------------

    def bouger(self, nom: str, angle: float, vitesse: int = 60) -> int:
        """Déplace une articulation. Renvoie l'angle réellement atteint après butées.

        vitesse : degrés par seconde (le firmware lisse le mouvement).
        """
        if nom not in self.articulations:
            raise KeyError(f"Articulation inconnue : {nom}")
        articulation = self.articulations[nom]
        angle_borne = articulation.borner(angle)
        vitesse = max(5, min(300, int(vitesse)))
        reponse = self._envoyer(
            f"S {articulation.canal} {articulation.angle_servo(angle_borne)} {vitesse}"
        )
        if reponse == "ESTOP":
            raise ArretUrgence("Arrêt d'urgence enfoncé")
        if reponse != "OK":
            raise RuntimeError(f"Réponse inattendue de l'Arduino : {reponse}")
        self.positions[nom] = angle_borne
        return angle_borne

    def bouger_plusieurs(self, cibles: dict, vitesse: int = 60) -> dict:
        return {nom: self.bouger(nom, angle, vitesse) for nom, angle in cibles.items()}

    def repos(self, vitesse: int = 40):
        self.bouger_plusieurs({nom: a.repos for nom, a in self.articulations.items()}, vitesse)

    def etat(self) -> dict:
        return {
            "arret_urgence": self.arret_urgence,
            "simulation": self.simulation,
            "positions": dict(self.positions),
        }

    def fermer(self):
        if self._serie is not None:
            self._serie.close()
