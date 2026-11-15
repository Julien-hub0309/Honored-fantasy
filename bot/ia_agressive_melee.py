"""IA agressive de mêlée : Monstres. Frappe fort, vise souvent le plus faible, ne se protège presque jamais."""
from bot.cible import melee, plus_faible, potion


def decider(combat, a):
    adv = combat.adversaires(a)
    r = combat.rng.random()
    if a.pv.ratio < 0.2 and r < 0.2 and not a.boss:
        return potion(a), {"type": "defendre"}
    cible = plus_faible(adv) if r < 0.55 else combat.rng.choice(adv)
    return potion(a), melee(cible)
