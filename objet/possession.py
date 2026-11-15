"""Possession : prend le contrôle d'un ennemi, qui attaque alors son propre camp. Animaux d'abord, humains ensuite."""
from combat.rang import Alteration
from objet import Sort, ev


class Possession(Sort):
    id = "possession"
    nom = "Possession"
    cout = 24
    cible = "ennemi"
    fx = "possession"
    description = "Contrôle un Monstre 2 tours ; les humains résistent (35 % avant le niveau 10, 80 % ensuite). Boss immunisés."

    def executer(self, combat, acteur, cibles):
        c = cibles[0]
        e = [ev("anim", fx="possession", acteur=acteur, cibles=[c])]
        if c.boss:
            return e + [ev("texte", texte=f"{c.nom} résiste à la possession !")]
        chance = 1.0 if c.classe.id == "monstre" else (0.8 if acteur.niveau >= 10 else 0.35)
        if combat.rng.random() > chance:
            return e + [ev("texte", texte=f"{c.nom} repousse votre esprit.")]
        c.rang.ajouter(Alteration("possede", "Possédé", 2 + (1 if acteur.niveau >= 14 else 0), positif=False))
        return e + [ev("statut", cible=c, texte="Possédé", positif=False)]
