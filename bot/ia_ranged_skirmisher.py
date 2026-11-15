"""IA tirailleur / contrôleur à distance : Officiers, Sorcières, Harponneurs.

- Officier  : grenade contre les groupes, focalise le plus faible, Réflexion sur soi.
- Sorcière  : Attriction sur la cible la plus agile, Blink sur la plus faible.
- Harponneur: Stop Time et Domino (avec temps de recharge).
"""
from bot.cible import melee, pistolet, plus_faible, plus_agile, plus_dangereux, peut_sort, potion
from combat import actions as act


def decider(combat, a):
    adv = combat.adversaires(a)
    rng = combat.rng
    p = potion(a)
    if peut_sort(combat, a, "stop_time") and len(adv) >= 2 and not a.cd.get("stop_time") and not combat.temps_fige and rng.random() < 0.55:
        a.cd["stop_time"] = 7
        return p, {"type": "magie", "sort": "stop_time"}
    if peut_sort(combat, a, "domino") and len(adv) >= 2 and not a.cd.get("domino") and not any(c.lien for c in adv):
        a.cd["domino"] = 5
        return p, {"type": "magie", "sort": "domino", "cibles": sorted(adv, key=lambda c: -c.pv.valeur)[:2]}
    if peut_sort(combat, a, "attriction"):
        cand = [c for c in adv if not c.rang.a("attriction")]
        if cand and rng.random() < 0.55:
            return p, {"type": "magie", "sort": "attriction", "cibles": [plus_agile(cand)]}
    if peut_sort(combat, a, "blink") and rng.random() < 0.7:
        return p, {"type": "magie", "sort": "blink", "cibles": [plus_faible(adv)]}
    if len(adv) >= 3 and act.peut(a, "grenade") and rng.random() < 0.7:
        return p, {"type": "attaquer", "arme": "grenade"}
    if peut_sort(combat, a, "reflexion") and not a.rang.a("reflexion") and rng.random() < 0.6:
        return p, {"type": "magie", "sort": "reflexion", "cibles": [a]}
    if "pistolet" in a.classe.equipement and rng.random() < 0.3:
        return p, pistolet(plus_faible(adv))
    return p, melee(plus_dangereux(adv) if rng.random() < 0.4 else plus_faible(adv))
