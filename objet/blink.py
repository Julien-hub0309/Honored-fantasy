"""Blink : téléportation offensive. Dégâts bruts garantis (ne peut ni échouer, ni être critique)."""
from objet import Sort, ev


class Blink(Sort):
    id = "blink"
    nom = "Blink"
    cout = 12
    cible = "ennemi"
    fx = "blink"
    description = "Téléportation offensive : dégâts bruts garantis (ignore la Résistance)."

    def executer(self, combat, acteur, cibles):
        cible = cibles[0]
        n = int(round((20 + acteur.stat("INT") * 2.5) * combat.rng.uniform(0.95, 1.05)))
        e = [ev("anim", fx="blink", acteur=acteur, cibles=[cible])]
        e += combat.infliger(acteur, cible, n, nature="brut")
        return e
