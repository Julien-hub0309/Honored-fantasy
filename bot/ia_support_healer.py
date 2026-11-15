"""IA de soutien : Moines. Galvanise l'escouade (Courage), boit des potions, grenade sur les groupes, se protège."""
from bot.cible import melee, pistolet, plus_faible, peut_sort, potion
from combat import actions as act


def decider(combat, a):
    adv = combat.adversaires(a)
    rng = combat.rng
    p = potion(a)
    if peut_sort(combat, a, "courage") and not a.rang.a("courage") and not a.cd.get("courage") and rng.random() < 0.8:
        a.cd["courage"] = 4
        return p, {"type": "magie", "sort": "courage"}
    if len(adv) >= 3 and act.peut(a, "grenade") and rng.random() < 0.6:
        return p, {"type": "attaquer", "arme": "grenade"}
    if a.pv.ratio < 0.3 and rng.random() < 0.4:
        return p, {"type": "defendre"}
    if rng.random() < 0.25:
        return p, pistolet(rng.choice(adv))
    return p, melee(plus_faible(adv))
