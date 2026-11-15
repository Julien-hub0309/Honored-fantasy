"""Longue portée (Dishonored 2) : grappin d'ombre. Attire et frappe une cible. Exploration : bond jusqu'à 8 cases."""
from classe import formules as F
from combat.rang import Alteration
from objet import Sort, ev


class LonguePortee(Sort):
    id = "longue_portee"
    nom = "Longue portée"
    cout = 20
    cible = "ennemi"
    fx = "blink"
    description = "Grappin d'ombre : forts dégâts magiques, 50 % d'étourdir (pas les boss). Hors combat : bond de 8 cases."

    def executer(self, combat, acteur, cibles):
        c = cibles[0]
        n = F.degats_magiques(22, acteur.stat("INT"), c.stat("RES"), combat.rng)
        e = [ev("anim", fx="blink", acteur=acteur, cibles=[c])] + combat.infliger(acteur, c, n, nature="mag")
        if c.vivant and not c.boss and combat.rng.random() < 0.5:
            c.rang.ajouter(Alteration("etourdi", "Étourdi", 1, positif=False))
            e.append(ev("statut", cible=c, texte="Étourdi", positif=False))
        return e
