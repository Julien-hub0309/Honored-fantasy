"""Dégâts et soins spéciaux (attaques signatures des boss, zones, soins sur soi)."""
from classe import formules as F
from objet import ev


def puissance(a, base, coef_int=3.0, coef_for=0.0, mult=1.0, rng=None):
    v = (base + a.stat("INT") * coef_int + a.stat("FOR") * coef_for) * mult
    return int(v * (rng.uniform(0.94, 1.06) if rng else 1.0))


def zone(combat, a, nom, base, mult=1.0, fx="explosion", nature="mag", coef_int=2.2, coef_for=0.0, extra=None):
    cibles = combat.adversaires(a)
    e = [ev("annonce", texte=f"{a.nom} : {nom} !"), ev("anim", fx=fx, acteur=a, cibles=list(cibles))]
    for c in cibles:
        e += combat.infliger(a, c, int(puissance(a, base, coef_int, coef_for, mult, combat.rng) * (1 - F.mitigation(c.stat("RES")) * 0.5)), nature)
        if extra and c.vivant:
            e += extra(c)
    return e


def cible_unique(combat, a, cible, nom, base, mult=1.0, fx="coup", nature="mag", coef_int=3.0, coef_for=0.0, crit=False):
    e = [ev("annonce", texte=f"{a.nom} : {nom} !"), ev("anim", fx=fx, acteur=a, cibles=[cible])]
    n = puissance(a, base, coef_int, coef_for, mult, combat.rng)
    n = int(n * (1 - F.mitigation(cible.stat("RES")) * (0.5 if nature == "mag" else 1.0)))
    return e + combat.infliger(a, cible, n, nature, crit)


def soin(a, pct, nom):
    n = a.pv.gagner(int(a.pv.maximum * pct))
    return [ev("annonce", texte=f"{a.nom} : {nom}"), ev("anim", fx="soin", acteur=a, cibles=[a]), ev("soin", cible=a, n=n, stat="PV")]


def tour(a):
    a.phase += 1
    return a.phase
