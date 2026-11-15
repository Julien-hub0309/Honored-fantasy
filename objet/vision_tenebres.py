"""Vision des ténèbres : voir à travers l'ombre. Combat : DEX +3 au groupe (4 tours). Exploration : voir à travers les murs."""
from combat.rang import Alteration
from objet import Sort, ev


class VisionTenebres(Sort):
    id = "vision_tenebres"
    nom = "Vision des ténèbres"
    cout = 10
    cible = "allies"
    fx = "buff"
    description = "Voit à travers l'ombre : DEX +3 au groupe (4 tours). Hors combat : voir à travers les murs."

    def executer(self, combat, acteur, cibles):
        e = [ev("anim", fx="buff", acteur=acteur, cibles=cibles)]
        for c in cibles:
            c.rang.ajouter(Alteration("vision", "Vision", 4, ajout={"DEX": 3}))
            e.append(ev("statut", cible=c, texte="DEX +3", positif=True))
        return e
