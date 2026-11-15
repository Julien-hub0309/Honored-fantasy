"""Attriction : dégâts magiques + l'Agilité de la cible tombe à 0 pendant 2 tours."""
from classe import formules as F
from combat.rang import Alteration
from objet import Sort, ev


class Attriction(Sort):
    id = "attriction"
    nom = "Attriction"
    cout = 14
    cible = "ennemi"
    fx = "attriction"
    description = "Dégâts magiques. Réduit l'Agilité de la cible à 0 pendant 2 tours."

    def executer(self, combat, acteur, cibles):
        cible = cibles[0]
        n = F.degats_magiques(14, acteur.stat("INT") * 0.85, cible.stat("RES"), combat.rng)
        e = [ev("anim", fx="attriction", acteur=acteur, cibles=[cible])]
        e += combat.infliger(acteur, cible, n, nature="mag")
        if cible.vivant:
            cible.rang.ajouter(Alteration("attriction", "Attriction", 2, fixe={"AGI": 0}, positif=False))
            e.append(ev("statut", cible=cible, texte="AGI 0", positif=False))
        return e
