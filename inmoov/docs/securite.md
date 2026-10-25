# Sécurité

Un bras InMoov pèse plusieurs kilos et ses servos d'épaule peuvent pincer fort. Un robot piloté par une IA peut aussi mal comprendre une demande. Ces règles sont là pour que ce ne soit jamais grave.

## Avant chaque séance

- [ ] Le bouton d'arrêt d'urgence est à portée de main, et testé : enfoncé, plus rien ne bouge et le programme dit « arrêt d'urgence ».
- [ ] Personne dans la zone des bras au démarrage (le robot se met en position de repos).
- [ ] Les câbles ne passent pas dans les articulations.

## Calibration (nouveau servo, servo démonté, pièce changée)

1. Servo **non relié** à la pièce : envoyer `S <canal> 90 30` depuis le moniteur série, puis fixer le palonnier à 90°.
2. Relier la pièce, puis approcher les butées par petits pas (5°), à vitesse lente (`30`).
3. Dès que le servo force ou grogne, revenir de 5° : c'est la butée. La noter en `min` / `max` dans `config.yaml`.
4. Ne jamais mettre des butées plus larges que ce qui a été testé à la main.

## Ce que fait déjà le programme

- **Butées vérifiées deux fois** : dans Python (config.yaml) et dans le firmware (0-180°).
- **Mouvements lissés** : le firmware limite la vitesse de chaque servo.
- **Arrêt d'urgence matériel** : il coupe le courant des servos, sans dépendre du logiciel.
- **Claude n'a que des outils limités** : il ne peut pas sortir des butées ni désactiver l'arrêt d'urgence, et on lui demande de bouger doucement près des gens.

## Règles

- Jamais d'enfant seul à côté du robot allumé.
- Ne pas laisser le robot allumé sans surveillance.
- Alimentation : fusibles, fils de bonne section, rien de dénudé. Le 230 V reste dans un boîtier fermé.
