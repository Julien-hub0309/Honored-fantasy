"""Attraction (DLC Daud) : attire ennemis (et objets hors combat). Dégâts légers et ennemis déséquilibrés."""
from classe import formules as F
from combat.rang import Alteration
from objet import Sort, ev


class Attirance(Sort):
    id = "attraction"
    nom = "Attraction"
    cout = 16
    cible = "ennemis"
    fx = "attriction"
    description = "Attire tous les ennemis : dégâts légers, AGI -3 et DEX -2 (2 tours). Hors combat : attire les objets proches."

    def executer(self, combat, acteur, cibles):
        e = [ev("anim", fx="attriction", acteur=acteur, cibles=list(cibles))]
        for c in list(cibles):
            e += combat.infliger(acteur, c, F.degats_magiques(8, acteur.stat("INT") * 0.5, c.stat("RES"), combat.rng), nature="mag")
            if c.vivant:
                c.rang.ajouter(Alteration("attire", "Attiré", 2, ajout={"AGI": -3, "DEX": -2}, positif=False))
                e.append(ev("statut", cible=c, texte="Attiré", positif=False))
        return e
