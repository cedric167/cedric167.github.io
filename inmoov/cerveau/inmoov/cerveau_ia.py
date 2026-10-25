"""Le cerveau : Claude reçoit ce qu'on dit au robot et décide quoi faire.

Claude ne commande jamais les servos directement. Il appelle des outils
(bouger une articulation, faire un geste, prendre une photo...) et ce
programme les exécute à travers Corps, qui applique les butées.
"""

import json
from pathlib import Path

import anthropic

from . import gestes
from .corps import ArretUrgence

FICHIER_MEMOIRE = Path(__file__).resolve().parent.parent / "memoire.json"

CONSIGNES = """Tu es le cerveau d'un robot humanoïde InMoov, imprimé en 3D, construit par Cédric.
Tu parles français, à voix haute : tes réponses sont lues par une synthèse vocale.
Fais des phrases courtes et naturelles, sans listes, sans markdown, sans emoji.

Ton corps : une tête (rotation, cou, mâchoire, yeux), deux bras (omoplate, épaule,
rotation, biceps, poignet) avec des mains à cinq doigts, et un torse. Tu ne marches pas.
Une caméra dans ton œil te permet de voir quand tu prends une photo.

Pour agir, utilise tes outils :
- prendre_photo quand tu as besoin de voir (on te montre quelque chose, on te demande qui est là...).
- faire_geste pour les gestes courants (saluer, hocher la tête, tendre la main...).
- bouger_articulations pour un mouvement précis. Les angles sont en degrés et chaque
  articulation a des butées : un angle hors limites est ramené à la butée.
- suivi_visage pour suivre du regard la personne en face de toi : tes yeux la suivent
  tout de suite, ta tête et ton cou suivent ensuite. Active-le dès que tu parles à quelqu'un.
- regarder pour tourner la tête et le cou dans une direction (cela arrête le suivi du visage).
- noter_souvenir pour retenir une information utile d'une conversation à l'autre
  (prénom d'une personne, préférence...).

Sécurité : bouge lentement quand quelqu'un est proche, ne fais pas de grands mouvements
de bras sans prévenir, et si un outil répond que l'arrêt d'urgence est enfoncé,
arrête de bouger et dis-le.

Articulations et butées (min-max, repos) :
{articulations}

Ce dont tu te souviens des conversations précédentes :
{souvenirs}"""


def _outils(noms_articulations: list) -> list:
    return [
        {
            "name": "bouger_articulations",
            "description": "Déplace une ou plusieurs articulations vers un angle en degrés. "
                           "Les angles sont ramenés aux butées de chaque articulation.",
            "strict": True,
            "input_schema": {
                "type": "object",
                "properties": {
                    "mouvements": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "articulation": {"type": "string", "enum": noms_articulations},
                                "angle": {"type": "number"},
                            },
                            "required": ["articulation", "angle"],
                            "additionalProperties": False,
                        },
                    },
                    "vitesse": {
                        "type": "integer",
                        "description": "Degrés par seconde, entre 5 et 300. 30 = lent et doux, 120 = vif.",
                    },
                },
                "required": ["mouvements", "vitesse"],
                "additionalProperties": False,
            },
        },
        {
            "name": "faire_geste",
            "description": "Joue un geste préenregistré.",
            "strict": True,
            "input_schema": {
                "type": "object",
                "properties": {"geste": {"type": "string", "enum": list(gestes.GESTES)}},
                "required": ["geste"],
                "additionalProperties": False,
            },
        },
        {
            "name": "prendre_photo",
            "description": "Prend une photo avec la caméra de l'œil et indique les visages détectés.",
            "strict": True,
            "input_schema": {"type": "object", "properties": {}, "required": [], "additionalProperties": False},
        },
        {
            "name": "suivi_visage",
            "description": "Active ou désactive le suivi automatique du visage le plus proche par la tête.",
            "strict": True,
            "input_schema": {
                "type": "object",
                "properties": {"actif": {"type": "boolean"}},
                "required": ["actif"],
                "additionalProperties": False,
            },
        },
        {
            "name": "regarder",
            "description": "Tourne la tête et le cou dans une direction et remet les yeux au milieu. "
                           "horizontal : -1 = tout à ta gauche, 0 = devant, +1 = tout à ta droite. "
                           "vertical : -1 = en bas, 0 = droit devant, +1 = en haut. "
                           "Désactive le suivi du visage.",
            "strict": True,
            "input_schema": {
                "type": "object",
                "properties": {"horizontal": {"type": "number"}, "vertical": {"type": "number"}},
                "required": ["horizontal", "vertical"],
                "additionalProperties": False,
            },
        },
        {
            "name": "etat_du_corps",
            "description": "Renvoie la position actuelle de chaque articulation et l'état de l'arrêt d'urgence.",
            "strict": True,
            "input_schema": {"type": "object", "properties": {}, "required": [], "additionalProperties": False},
        },
        {
            "name": "noter_souvenir",
            "description": "Enregistre une information à retenir pour les prochaines conversations.",
            "strict": True,
            "input_schema": {
                "type": "object",
                "properties": {"souvenir": {"type": "string"}},
                "required": ["souvenir"],
                "additionalProperties": False,
            },
        },
    ]


class Cerveau:
    def __init__(self, config: dict, corps, vision, voix):
        self.config = config["ia"]
        self.corps = corps
        self.vision = vision
        self.voix = voix
        self.client = anthropic.Anthropic()  # lit ANTHROPIC_API_KEY dans l'environnement
        self.outils = _outils(list(corps.articulations))
        self.nouvelle_conversation()

    # --- Conversation ----------------------------------------------------

    def nouvelle_conversation(self):
        articulations = "\n".join(
            f"- {a.nom} : {a.min}-{a.max}, repos {a.repos}" for a in self.corps.articulations.values()
        )
        souvenirs = "\n".join(f"- {s}" for s in self._lire_souvenirs()) or "(rien pour l'instant)"
        # Le prompt système reste identique pendant toute la conversation, ce qui permet
        # au cache de l'API de resservir le début de chaque requête à moindre coût.
        self.systeme = CONSIGNES.format(articulations=articulations, souvenirs=souvenirs)
        self.messages = []
        self.echanges = 0

    def repondre(self, texte_entendu: str):
        """Traite une phrase entendue : Claude réfléchit, agit, parle, jusqu'à avoir fini."""
        if self.echanges >= self.config["echanges_max"]:
            self.nouvelle_conversation()
        self.echanges += 1
        self.messages.append({"role": "user", "content": texte_entendu})

        while True:
            reponse = self._appeler_claude()
            if reponse is None:
                self.voix.parler("Je n'arrive pas à joindre mon cerveau. Vérifie la connexion internet.")
                return
            # On renvoie toujours le contenu complet de la réponse (pas seulement le texte).
            self.messages.append({"role": "assistant", "content": reponse.content})

            for bloc in reponse.content:
                if bloc.type == "text" and bloc.text.strip():
                    self.voix.parler(bloc.text)

            if reponse.stop_reason == "refusal":
                self.voix.parler("Je préfère ne pas faire ça.")
                return
            if reponse.stop_reason == "max_tokens":
                self.voix.parler("Je me suis perdu dans mes pensées, tu peux répéter ?")
                return
            if reponse.stop_reason == "pause_turn":
                continue
            if reponse.stop_reason != "tool_use":
                return

            resultats = [
                self._executer(bloc) for bloc in reponse.content if bloc.type == "tool_use"
            ]
            # Tous les résultats d'outils repartent ensemble, dans un seul message.
            self.messages.append({"role": "user", "content": resultats})

    def _appeler_claude(self):
        try:
            return self.client.beta.messages.create(
                model=self.config["modele"],
                max_tokens=self.config["max_tokens"],
                output_config={"effort": self.config["effort"]},
                cache_control={"type": "ephemeral"},
                # Si Claude décline une demande, l'API la repasse automatiquement
                # à un modèle de secours plutôt que de s'arrêter net.
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
                system=self.systeme,
                tools=self.outils,
                messages=self.messages,
            )
        except anthropic.AuthenticationError:
            print("Clé API invalide : vérifie ANTHROPIC_API_KEY dans le fichier .env")
        except anthropic.RateLimitError:
            print("Trop de requêtes : attends un peu.")
        except anthropic.APIStatusError as erreur:
            print(f"Erreur de l'API ({erreur.status_code}) : {erreur.message}")
        except anthropic.APIConnectionError:
            print("Pas de connexion à l'API Claude.")
        # L'appel a échoué : on retire la question restée sans réponse pour que
        # l'historique reste valide (un message utilisateur, puis une réponse).
        if self.messages and self.messages[-1]["role"] == "user" and isinstance(self.messages[-1]["content"], str):
            self.messages.pop()
        return None

    # --- Outils ----------------------------------------------------------

    def _executer(self, bloc) -> dict:
        try:
            contenu = self._outil(bloc.name, bloc.input)
            return {"type": "tool_result", "tool_use_id": bloc.id, "content": contenu}
        except ArretUrgence:
            message = "Arrêt d'urgence enfoncé : aucun mouvement n'est possible."
        except Exception as erreur:
            message = f"Erreur : {erreur}"
        return {"type": "tool_result", "tool_use_id": bloc.id, "content": message, "is_error": True}

    def _outil(self, nom: str, entree: dict):
        if nom == "bouger_articulations":
            cibles = {m["articulation"]: m["angle"] for m in entree["mouvements"]}
            atteints = self.corps.bouger_plusieurs(cibles, vitesse=entree["vitesse"])
            return json.dumps({"angles_atteints": atteints}, ensure_ascii=False)

        if nom == "faire_geste":
            gestes.jouer(self.corps, entree["geste"])
            return f"Geste « {entree['geste']} » effectué."

        if nom == "prendre_photo":
            photo = self.vision.photo_jpeg_base64() if self.vision else None
            if photo is None:
                return "Aucune caméra disponible."
            visages = json.dumps(self.vision.visages(), ensure_ascii=False)
            return [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": photo}},
                {"type": "text", "text": f"Visages détectés (horizontal -1 = à ta gauche, +1 = à ta droite) : {visages}"},
            ]

        if nom == "suivi_visage":
            if not self.vision or not self.vision.disponible:
                return "Aucune caméra disponible."
            self.vision.suivi_actif = entree["actif"]
            return "Suivi du visage activé." if entree["actif"] else "Suivi du visage désactivé."

        if nom == "regarder":
            if self.vision:
                self.vision.suivi_actif = False
            # Dans config.yaml, un angle plus grand veut dire vers la gauche et vers le haut.
            cibles = {
                "tete_rotation": self._angle_direction("tete_rotation", -entree["horizontal"]),
                "cou": self._angle_direction("cou", entree["vertical"]),
                "yeux_horizontal": self.corps.articulations["yeux_horizontal"].repos,
                "yeux_vertical": self.corps.articulations["yeux_vertical"].repos,
            }
            atteints = self.corps.bouger_plusieurs(cibles, vitesse=60)
            return json.dumps({"angles_atteints": atteints}, ensure_ascii=False)

        if nom == "etat_du_corps":
            return json.dumps(self.corps.etat(), ensure_ascii=False)

        if nom == "noter_souvenir":
            souvenirs = self._lire_souvenirs()
            souvenirs.append(entree["souvenir"])
            FICHIER_MEMOIRE.write_text(json.dumps(souvenirs, ensure_ascii=False, indent=2), encoding="utf-8")
            return "Souvenir enregistré."

        raise ValueError(f"Outil inconnu : {nom}")

    def _angle_direction(self, nom: str, valeur: float) -> float:
        """Convertit une direction de -1 à +1 en angle, entre les butées de l'articulation."""
        a = self.corps.articulations[nom]
        valeur = max(-1.0, min(1.0, valeur))
        return a.repos + valeur * ((a.max - a.repos) if valeur > 0 else (a.repos - a.min))

    @staticmethod
    def _lire_souvenirs() -> list:
        if not FICHIER_MEMOIRE.exists():
            return []
        try:
            return json.loads(FICHIER_MEMOIRE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
