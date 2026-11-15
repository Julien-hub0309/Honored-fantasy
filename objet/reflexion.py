"""Réflexion : Intelligence et Dextérité +2 (durée par défaut : 3 tours)."""
from combat.rang import Alteration
from objet import Sort, ev

DUREE = 3


def appliquer(cible):
    cible.rang.ajouter(Alteration("reflexion", "Réflexion", DUREE, ajout={"INT": 2, "DEX": 2}))


class Reflexion(Sort):
    id = "reflexion"
    nom = "Réflexion"
    cout = 12
    cible = "allies"
    fx = "buff"
    description = "INT et DEX +2 pendant 3 tours pour tout le groupe."

    def executer(self, combat, acteur, cibles):
        e = [ev("anim", fx="buff", acteur=acteur, cibles=cibles)]
        for c in cibles:
            appliquer(c)
            e.append(ev("statut", cible=c, texte="INT/DEX +2", positif=True))
        return e
