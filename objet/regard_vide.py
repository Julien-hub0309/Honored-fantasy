"""Regard du Vide (DLC Daud) : dévoile les failles des ennemis. Exploration : détecte les Runes (boss) et les coffres."""
from combat.rang import Alteration
from objet import Sort, ev


class RegardVide(Sort):
    id = "regard_vide"
    nom = "Regard du Vide"
    cout = 14
    cible = "ennemis"
    fx = "attriction"
    description = "Révèle les ennemis : RES -3 et AGI -2 (3 tours). Hors combat : détecte Runes et coffres."

    def executer(self, combat, acteur, cibles):
        e = [ev("anim", fx="attriction", acteur=acteur, cibles=list(cibles))]
        for c in cibles:
            c.rang.ajouter(Alteration("revele", "Révélé", 3, ajout={"RES": -3, "AGI": -2}, positif=False))
            e.append(ev("statut", cible=c, texte="Révélé", positif=False))
        return e
