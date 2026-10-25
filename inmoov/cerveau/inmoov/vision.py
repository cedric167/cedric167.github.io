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
            if self.suivi_actif and len(visages):
                self._suivre(image, max(visages, key=lambda v: v[2] * v[3]))
            time.sleep(1 / 15)

    def _suivre(self, image, visage):
        """Tourne la tête pour garder le plus grand visage au centre de l'image."""
        hauteur, largeur = image.shape[:2]
        x, y, l, h = visage
        ecart_x = (x + l / 2) - largeur / 2
        ecart_y = (y + h / 2) - hauteur / 2
        zone_morte = self.reglages["zone_morte"]
        try:
            if abs(ecart_x) > zone_morte:
                cible = self.corps.positions["tete_rotation"] - ecart_x * self.reglages["gain_horizontal"]
                self.corps.bouger("tete_rotation", cible, vitesse=120)
            if abs(ecart_y) > zone_morte:
                cible = self.corps.positions["cou"] - ecart_y * self.reglages["gain_vertical"]
                self.corps.bouger("cou", cible, vitesse=120)
        except Exception:
            # Arrêt d'urgence ou souci série : le réflexe s'arrête, Claude sera prévenu au prochain mouvement.
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
