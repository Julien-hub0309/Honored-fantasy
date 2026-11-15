"""Potion de Vie (50 % des PV max) et Potion de Vie+ (100 %)."""
POURCENTAGES = {"potion_vie": 0.5, "potion_vie_plus": 1.0}


def soigner(cible, pourcentage):
    mult = cible.classe.efficacite_potion
    return cible.pv.gagner(int(cible.pv.maximum * pourcentage * mult))
