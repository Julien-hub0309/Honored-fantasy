"""Stop Time : gèle le temps. Personne ne peut agir pendant 2 tours, sauf le lanceur."""
from objet import Sort, ev


class StopTime(Sort):
    id = "stop_time"
    nom = "Stop Time"
    cout = 30
    cible = "soi"
    fx = "temps"
    description = "Fige toutes les autres entités pendant 2 tours (les boss ne sont figés qu'un tour)."

    def executer(self, combat, acteur, cibles):
        combat.temps_fige = {"lanceur": acteur, "restant": 2, "ce_tour": True}
        return [ev("anim", fx="temps", acteur=acteur, cibles=[]), ev("texte", texte="Le temps s'arrête...")]
