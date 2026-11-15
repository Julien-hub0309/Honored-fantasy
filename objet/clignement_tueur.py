"""Clignement du Tueur (DLC Daud) : frappe téléportée qui fige la cible dans le temps (un tour perdu)."""
from combat.rang import Alteration
from objet import Sort, ev


class ClignementTueur(Sort):
    id = "clignement_tueur"
    nom = "Clignement du Tueur"
    cout = 20
    cible = "ennemi"
    fx = "blink"
    description = "Blink qui fige la cible : dégâts bruts garantis, un tour perdu (pas les boss)."

    def executer(self, combat, acteur, cibles):
        c = cibles[0]
        n = int(round((22 + acteur.stat("INT") * 2.8) * combat.rng.uniform(0.95, 1.05)))
        e = [ev("anim", fx="blink", acteur=acteur, cibles=[c])] + combat.infliger(acteur, c, n, nature="brut")
        if c.vivant and not c.boss:
            c.rang.ajouter(Alteration("etourdi", "Figé", 1, positif=False))
            e.append(ev("statut", cible=c, texte="Figé", positif=False))
        return e
