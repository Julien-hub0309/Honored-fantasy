"""Arme de corps à corps : dégâts basés sur la Force + dégâts de base de l'arme ; Dextérité (toucher/critique) vs Agilité adverse."""


def resoudre(acteur, cible, rng):
    """Retourne (touche, critique). Les dégâts sont calculés par la classe (classe/formules.py)."""
    dex, agi = acteur.stat("DEX"), cible.stat("AGI")
    if rng.random() > acteur.classe.toucher_melee(dex, agi):
        return False, False
    bonus = 0.05 if acteur.a_passif("meurtrier_ombre") else 0.0
    return True, rng.random() < acteur.classe.critique_melee(dex, agi) + bonus
