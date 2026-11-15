"""Choix de cibles et d'actions élémentaires partagés par les IA."""


def plus_faible(cibles):
    return min(cibles, key=lambda c: c.pv.valeur)


def plus_agile(cibles):
    return max(cibles, key=lambda c: c.stat("AGI"))


def plus_dangereux(cibles):
    return max(cibles, key=lambda c: c.stat("FOR") + c.stat("INT"))


def plus_vigoureux(cibles):
    return max(cibles, key=lambda c: c.pv.valeur)


def melee(cible):
    return {"type": "attaquer", "arme": "melee", "cible": cible}


def pistolet(cible):
    return {"type": "attaquer", "arme": "pistolet", "cible": cible}


def peut_sort(combat, a, sort_id):
    from combat.actions import SORTS
    return sort_id in a.sorts and a.mana.valeur >= a.cout_sort(SORTS[sort_id])


def potion(a):
    """Phase d'objet : boit une potion de vie si peu de PV. Retourne (objet, cible) ou None."""
    if a.inventaire and a.pv.ratio < 0.4:
        for o in a.inventaire:
            if "pv_pct" in o.effet:
                return (o, a)
    return None
