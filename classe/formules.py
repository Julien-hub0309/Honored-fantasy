"""Formules mathématiques du combat (cahier des charges §8.4 : formules exactes).

Toutes les stats passées en argument sont des stats *effectives* (buffs / debuffs / posture déjà appliqués).

  Dégâts physiques = (dégâts_base + FOR x 3) x multiplicateur x (1 - RES_cible / (RES_cible + 12)) x variance(0.92..1.08)
                     coup critique : x 1.8
  Toucher          = clamp(base + (DEX_att - AGI_cible) x 0.04, 0.25, 0.97)
  Critique         = clamp(0.05 + DEX x 0.012 - AGI_cible x 0.006 + bonus, 0, 0.6)       (l'AGI évite les critiques)
  Dégâts magiques  = (base + INT x 3) x variance, ignorent la moitié de la RES
  Coût en mana     = coût_base x clamp(1 - INT x 0.03, 0.4, 1)
  Fuite            = clamp(0.5 x (AGI_lanceur + 2) / (AGI_moyenne_ennemis + 2) + bonus, 0.10, 0.95)
"""
import random

CRIT_MULT = 1.8


def mitigation(res):
    return max(0.0, res) / (max(0.0, res) + 12.0)


def variance(rng=random):
    return rng.uniform(0.92, 1.08)


def clamp(v, a, b):
    return max(a, min(b, v))


def degats_physiques(base, force, res_cible, mult=1.0, critique=False, rng=random):
    brut = (base + force * 3.0) * mult * variance(rng)
    if critique:
        brut *= CRIT_MULT
    return max(1, int(round(brut * (1.0 - mitigation(res_cible)))))


def degats_magiques(base, intel, res_cible=0.0, rng=random):
    brut = (base + intel * 3.0) * variance(rng)
    return max(1, int(round(brut * (1.0 - mitigation(res_cible) * 0.5))))


def chance_toucher(dex, agi_cible, base=0.85):
    return clamp(base + (dex - agi_cible) * 0.04, 0.25, 0.97)


def chance_critique(dex, agi_cible, bonus=0.0):
    return clamp(0.05 + dex * 0.012 - agi_cible * 0.006 + bonus, 0.0, 0.6)


def cout_mana(cout_base, intel, reduction_classe=0.0):
    return max(1, int(round(cout_base * clamp(1 - intel * 0.03 - reduction_classe, 0.4, 1.0))))


def chance_fuite(agi_lanceur, agi_ennemis, bonus=0.0):
    moy = sum(agi_ennemis) / max(1, len(agi_ennemis))
    return clamp(0.5 * (agi_lanceur + 2) / (moy + 2) + bonus, 0.10, 0.95)


def stats_au_niveau(base, croissance, niveau):
    return {k: int(base[k] + croissance.get(k, 0) * (niveau - 1)) for k in base}


def xp_requis(niveau):
    """XP nécessaire pour passer du niveau `niveau` au suivant."""
    return int(30 * niveau ** 1.65)
