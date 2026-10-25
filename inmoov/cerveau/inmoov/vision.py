"""Les yeux du robot : caméra, détection de visages et suivi du regard.

Le suivi tourne en local, environ 15 fois par seconde, parce qu'un appel à
Claude prend une ou deux secondes : c'est le réflexe. Claude, lui, demande une
photo quand il veut comprendre ce qu'il voit.
"""

import base64
import threading
import time

import cv2


class Vision:
    def __init__(self, config: dict, corps):
        self.corps = corps
        self.reglages = config["suivi_visage"]
        materiel = config["materiel"]
        self.camera = cv2.VideoCapture(materiel.get("camera", 0))
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, materiel.get("camera_largeur", 640))
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, materiel.get("camera_hauteur", 480))
        self.disponible = self.camera.isOpened()
        self.detecteur = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        self.suivi_actif = False
        self._image = None
        self._visages = []
        self._dernier_visage = 0.0
        self._verrou = threading.Lock()
        self._en_marche = self.disponible
        if self.disponible:
            threading.Thread(target=self._boucle, daemon=True).start()

    def _boucle(self):
        while self._en_marche:
            ok, image = self.camera.read()
            if not ok:
                time.sleep(0.1)
                continue
            gris = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            visages = self.detecteur.detectMultiScale(gris, scaleFactor=1.2, minNeighbors=5, minSize=(60, 60))
            with self._verrou:
                self._image = image
                self._visages = [tuple(int(v) for v in visage) for visage in visages]
            if self.suivi_actif:
                if len(visages):
                    hauteur, largeur = image.shape[:2]
                    x, y, l, h = max(visages, key=lambda v: v[2] * v[3])
                    # Écart du visage par rapport au centre de l'image, de -1 à +1.
                    self.suivre(((x + l / 2) - largeur / 2) / (largeur / 2),
                                ((y + h / 2) - hauteur / 2) / (hauteur / 2))
                elif time.monotonic() - self._dernier_visage > self.reglages["delai_perte"]:
                    self._recentrer_yeux()
            time.sleep(1 / 15)

    def suivre(self, ecart_x: float, ecart_y: float):
        """Un pas de suivi du regard, appelé à chaque image où un visage est vu.

        Comme chez un humain, les yeux réagissent tout de suite pour garder le
        visage au centre de l'image (la caméra est dans l'œil). La tête et le
        cou suivent plus lentement, dans la direction où les yeux sont tournés :
        en tournant, ils ramènent peu à peu les yeux vers le milieu.
        """
        self._dernier_visage = time.monotonic()
        r = self.reglages
        pos = self.corps.positions
        try:
            if abs(ecart_x) > r["zone_morte"]:
                self.corps.bouger("yeux_horizontal", pos["yeux_horizontal"] - ecart_x * r["gain_yeux_horizontal"], vitesse=200)
            if abs(ecart_y) > r["zone_morte"]:
                self.corps.bouger("yeux_vertical", pos["yeux_vertical"] - ecart_y * r["gain_yeux_vertical"], vitesse=200)

            decalage_h = pos["yeux_horizontal"] - self.corps.articulations["yeux_horizontal"].repos
            if abs(decalage_h) > r["tolerance_yeux"]:
                self.corps.bouger("tete_rotation", pos["tete_rotation"] + decalage_h * r["gain_tete"], vitesse=60)
            decalage_v = pos["yeux_vertical"] - self.corps.articulations["yeux_vertical"].repos
            if abs(decalage_v) > r["tolerance_yeux"]:
                self.corps.bouger("cou", pos["cou"] + decalage_v * r["gain_cou"], vitesse=40)
        except Exception:
            # Arrêt d'urgence ou souci série : le réflexe s'arrête, Claude sera prévenu au prochain mouvement.
            self.suivi_actif = False

    def _recentrer_yeux(self):
        """Plus de visage depuis un moment : les yeux reviennent doucement au milieu."""
        try:
            for nom in ("yeux_horizontal", "yeux_vertical"):
                repos = self.corps.articulations[nom].repos
                if self.corps.positions[nom] != repos:
                    self.corps.bouger(nom, repos, vitesse=40)
        except Exception:
            self.suivi_actif = False

    def visages(self) -> list:
        """Visages vus en ce moment : position horizontale (-1 gauche, +1 droite) et taille relative."""
        with self._verrou:
            if self._image is None:
                return []
            hauteur, largeur = self._image.shape[:2]
            return [
                {
                    "horizontal": round((x + l / 2) / largeur * 2 - 1, 2),
                    "vertical": round((y + h / 2) / hauteur * 2 - 1, 2),
                    "taille": round(l / largeur, 2),
                }
                for x, y, l, h in self._visages
            ]

    def photo_jpeg_base64(self):
        """Dernière image de la caméra, en JPEG encodé base64 (None si pas de caméra)."""
        with self._verrou:
            if self._image is None:
                return None
            ok, jpeg = cv2.imencode(".jpg", self._image, [cv2.IMWRITE_JPEG_QUALITY, 80])
        return base64.standard_b64encode(jpeg.tobytes()).decode("ascii") if ok else None

    def fermer(self):
        self._en_marche = False
        self.camera.release()
