"""Envoûtement (Dishonored 2) : hypnotise un ennemi 2 tours ; il se réveille s'il est blessé."""
from combat.rang import Alteration
from objet import Sort, ev


class Envoutement(Sort):
    id = "envoutement"
    nom = "Envoûtement"
    cout = 22
    cible = "ennemi"
    fx = "attriction"
    description = "Hypnotise un ennemi 2 tours (85 %). Il se réveille s'il subit des dégâts. Boss immunisés."

    def executer(self, combat, acteur, cibles):
        c = cibles[0]
        e = [ev("anim", fx="attriction", acteur=acteur, cibles=[c])]
        if c.boss or combat.rng.random() > 0.85:
            return e + [ev("texte", texte=f"{c.nom} ne succombe pas.")]
        c.rang.ajouter(Alteration("hypnotise", "Hypnotisé", 2, positif=False))
        return e + [ev("statut", cible=c, texte="Hypnotisé", positif=False)]
