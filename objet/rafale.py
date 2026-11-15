"""Rafale : bourrasque d'air. Dégâts à tous les ennemis, 40 % de chance d'étourdir (un tour perdu)."""
from classe import formules as F
from combat.rang import Alteration
from objet import Sort, ev


class Rafale(Sort):
    id = "rafale"
    nom = "Rafale"
    cout = 18
    cible = "ennemis"
    fx = "rafale"
    description = "Bourrasque : dégâts à tous les ennemis, 40 % d'étourdir (pas les boss)."

    def executer(self, combat, acteur, cibles):
        e = [ev("anim", fx="rafale", acteur=acteur, cibles=list(cibles))]
        for c in list(cibles):
            e += combat.infliger(acteur, c, F.degats_magiques(10, acteur.stat("INT") * 0.6, c.stat("RES"), combat.rng), nature="mag")
            if c.vivant and not c.boss and combat.rng.random() < 0.4:
                c.rang.ajouter(Alteration("etourdi", "Étourdi", 1, positif=False))
                e.append(ev("statut", cible=c, texte="Étourdi", positif=False))
        return e
