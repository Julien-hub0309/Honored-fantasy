"""Nuée vorace : invoque des rats qui rongent tous les ennemis (dégâts sur 3 tours)."""
from classe import formules as F
from combat.rang import Alteration
from objet import Sort, ev


class NueeVorace(Sort):
    id = "nuee_vorace"
    nom = "Nuée vorace"
    cout = 20
    cible = "ennemis"
    fx = "rats"
    description = "Une nuée de rats : petits dégâts, puis les ennemis sont rongés pendant 3 tours."

    def executer(self, combat, acteur, cibles):
        e = [ev("anim", fx="rats", acteur=acteur, cibles=list(cibles))]
        dot = int(5 + acteur.stat("INT") * 1.0)
        for c in list(cibles):
            e += combat.infliger(acteur, c, F.degats_magiques(6, acteur.stat("INT") * 0.4, c.stat("RES"), combat.rng), nature="mag")
            if c.vivant:
                c.rang.ajouter(Alteration("nuee", "Rongé", 3, positif=False, dot=dot))
                e.append(ev("statut", cible=c, texte="Rongé", positif=False))
        return e
