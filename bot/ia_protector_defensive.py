"""IA protectrice / défensive : Gardes Urbains. Tient la ligne, tire à l'occasion, se met en garde quand il faiblit."""
from bot.cible import melee, pistolet, plus_faible, peut_sort, potion


def decider(combat, a):
    adv = combat.adversaires(a)
    rng = combat.rng
    p = potion(a)
    if peut_sort(combat, a, "courage") and not a.rang.a("courage") and not a.cd.get("courage") and rng.random() < 0.7:
        a.cd["courage"] = 4
        return p, {"type": "magie", "sort": "courage"}
    if a.pv.ratio < 0.35 and rng.random() < 0.45:
        return p, {"type": "defendre"}
    if "pistolet" in a.classe.equipement and rng.random() < 0.28:
        return p, pistolet(rng.choice(adv))
    return p, melee(plus_faible(adv) if rng.random() < 0.55 else rng.choice(adv))
