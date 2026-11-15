"""Potion de Mana (50 % du Mana max) et Potion de Mana+ (100 %)."""
POURCENTAGES = {"potion_mana": 0.5, "potion_mana_plus": 1.0}


def restaurer(cible, pourcentage):
    return cible.mana.gagner(int(cible.mana.maximum * pourcentage))
