"""Les oreilles et la bouche du robot.

- écoute : micro + reconnaissance vocale (SpeechRecognition, service Google gratuit)
- parole : synthèse vocale hors ligne (pyttsx3), avec la mâchoire qui bouge
- mode texte : clavier et écran, pour tester sans micro ni haut-parleur
"""

import threading
import time


class Voix:
    def __init__(self, config: dict, corps, mode_texte: bool = False):
        self.corps = corps
        self.langue = config["voix"]["langue"]
        self.mode_texte = mode_texte
        if mode_texte:
            return
        import pyttsx3
        import speech_recognition as sr

        self._sr = sr
        self.reconnaissance = sr.Recognizer()
        self.micro = sr.Microphone()
        with self.micro as source:
            self.reconnaissance.adjust_for_ambient_noise(source, duration=1)
        self.synthese = pyttsx3.init()
        self.synthese.setProperty("rate", config["voix"]["vitesse_parole"])
        for voix in self.synthese.getProperty("voices"):
            if "fr" in (voix.id + voix.name).lower():
                self.synthese.setProperty("voice", voix.id)
                break

    def ecouter(self):
        """Attend une phrase. Renvoie le texte, ou None si rien de compréhensible."""
        if self.mode_texte:
            try:
                return input("\nToi > ").strip() or None
            except EOFError:
                return "au revoir"
        with self.micro as source:
            try:
                audio = self.reconnaissance.listen(source, timeout=10, phrase_time_limit=15)
            except self._sr.WaitTimeoutError:
                return None
        try:
            return self.reconnaissance.recognize_google(audio, language=self.langue)
        except (self._sr.UnknownValueError, self._sr.RequestError):
            return None

    def parler(self, texte: str):
        print(f"\nRobot > {texte}")
        if self.mode_texte:
            return
        bouche_active = threading.Event()
        bouche_active.set()
        threading.Thread(target=self._bouger_machoire, args=(bouche_active,), daemon=True).start()
        try:
            self.synthese.say(texte)
            self.synthese.runAndWait()
        finally:
            bouche_active.clear()

    def _bouger_machoire(self, actif: threading.Event):
        machoire = self.corps.articulations["machoire"]
        ouverte = True
        try:
            while actif.is_set():
                self.corps.bouger("machoire", machoire.max if ouverte else machoire.min, vitesse=250)
                ouverte = not ouverte
                time.sleep(0.15)
            self.corps.bouger("machoire", machoire.repos, vitesse=250)
        except Exception:
            pass  # la parole continue même si la mâchoire est bloquée (arrêt d'urgence)
