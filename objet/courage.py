"""Courage : Force et Résistance +2 pendant 3 tours (toute l'équipe)."""
from combat.rang import Alteration
from objet import Sort, ev


def appliquer(cible):
    cible.rang.ajouter(Alteration("courage", "Courage", 3, ajout={"FOR": 2, "RES": 2}))


class Courage(Sort):
    id = "courage"
    nom = "Courage"
    cout = 14
    cible = "allies"
    fx = "buff"
    description = "FOR et RES +2 pendant 3 tours pour tout le groupe."

    def executer(self, combat, acteur, cibles):
        e = [ev("anim", fx="buff", acteur=acteur, cibles=cibles)]
        for c in cibles:
            appliquer(c)
            e.append(ev("statut", cible=c, texte="FOR/RES +2", positif=True))
        return e
