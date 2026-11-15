"""Pouvoirs, armes et consommables. Chaque module décrit un objet/pouvoir du cahier des charges (§3.2)."""
import random

from combat.rang import Alteration


class Sort:
    """Base d'un pouvoir. `cible` : ennemi | ennemis | deux_ennemis | allie | allies | soi"""
    id = ""
    nom = ""
    cout = 0
    cible = "ennemi"
    description = ""
    fx = "magie"

    def executer(self, combat, acteur, cibles):
        raise NotImplementedError


def ev(t, **kw):
    kw["t"] = t
    return kw
