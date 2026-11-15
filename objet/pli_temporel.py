"""Pli temporel : ralentit le temps (étape 1). L'arrêt complet est Stop Time (objet/stop_time.py)."""
from combat.rang import Alteration
from objet import Sort, ev


class PliTemporel(Sort):
    id = "pli_temporel"
    nom = "Pli temporel"
    cout = 18
    cible = "ennemis"
    fx = "temps"
    description = "Ralentit le temps : AGI -4 pour tous les ennemis pendant 3 tours (l'arrêt total est Stop Time)."

    def executer(self, combat, acteur, cibles):
        e = [ev("anim", fx="temps", acteur=acteur, cibles=list(cibles))]
        for c in cibles:
            c.rang.ajouter(Alteration("ralenti", "Ralenti", 3, ajout={"AGI": -4}, positif=False))
            e.append(ev("statut", cible=c, texte="Ralenti", positif=False))
        return e
