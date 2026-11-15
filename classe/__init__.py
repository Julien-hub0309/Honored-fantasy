"""Registre des classes + définition commune (ClasseDef). Les formules sont dans classe/formules.py.

Une classe = un fichier (garde_urbain.py, officier.py, ...) qui expose CLASSE.
"""
import importlib
import random
from dataclasses import dataclass, field
from typing import Dict, List

PASSIFS = {
    "agilite": ("Agilité", "AGI +2."),
    "soif_de_sang": ("Soif de sang", "Soigne 6 % des dégâts infligés, +12 % des PV max sur un coup fatal."),
    "vitalite": ("Vitalité", "PV max +15 %."),
    "meurtrier_ombre": ("Meurtrier de l'ombre", "+15 % de dégâts sur cibles affaiblies (malus, lien, temps figé), +5 % de critique."),
}
IDS = ["garde_urbain", "officier", "sorciere", "moine", "harponneur", "monstre"]
JOUABLES = ["garde_urbain", "officier", "sorciere", "moine", "harponneur"]


@dataclass
class ClasseDef:
    id: str
    nom: str
    role: str
    description: str
    stats_base: Dict[str, int]
    croissance: Dict[str, float]
    arme: dict
    equipement: List[str]
    sorts_par_niveau: Dict[int, str]
    mult_defense: float
    reduction_passive: float
    bonus_fuite: float
    bonus_critique: float
    bonus_grenade: float
    regen_pv: float
    reduction_mana: float
    efficacite_potion: float
    passif: str
    sprite: str
    biomes: List[str] = field(default_factory=list)
    jouable: bool = True
    passifs_par_niveau: Dict[int, str] = field(default_factory=dict)

    # ---- progression ----
    def stats(self, niveau):
        from classe.formules import stats_au_niveau
        return stats_au_niveau(self.stats_base, self.croissance, niveau)

    def sorts(self, niveau):
        return [s for lv, s in sorted(self.sorts_par_niveau.items()) if lv <= niveau]

    def passifs(self, niveau):
        return [p for lv, p in sorted(self.passifs_par_niveau.items()) if lv <= niveau]

    def appliquer_passifs(self, stats, niveau):
        """Passifs de l'Outsider qui modifient les stats : Agilité (AGI +2), Vitalité (PV max +15 %)."""
        ps = self.passifs(niveau)
        if "agilite" in ps:
            stats["AGI"] += 2
        if "vitalite" in ps:
            stats["PV"] = int(stats["PV"] * 1.15)
        return stats

    # ---- mécaniques de combat propres à la classe (formules : classe/formules.py) ----
    def toucher_melee(self, dex, agi_cible):
        from classe import formules as F
        return F.chance_toucher(dex, agi_cible, 0.85)

    def toucher_pistolet(self, dex, agi_cible):
        """Pistolet : haut risque. Un coup qui touche est TOUJOURS critique."""
        from classe import formules as F
        return F.chance_toucher(dex, agi_cible, 0.45)

    def critique_melee(self, dex, agi_cible):
        from classe import formules as F
        return F.chance_critique(dex, agi_cible, self.bonus_critique)

    def degats_melee(self, arme_base, force, res_cible, critique=False, rng=random):
        from classe import formules as F
        return F.degats_physiques(arme_base, force, res_cible, 1.0, critique, rng)

    def degats_pistolet(self, force, res_cible, rng=random):
        from classe import formules as F
        return F.degats_physiques(14, force * 0.6, res_cible, 1.0, True, rng)

    def degats_grenade(self, intel, res_cible, rng=random):
        from classe import formules as F
        base = F.degats_magiques(18, intel * 0.5, res_cible * 0.5, rng)
        return max(1, int(base * (1 + self.bonus_grenade)))

    def probabilite_fuite(self, agi, agi_ennemis):
        from classe import formules as F
        return F.chance_fuite(agi, agi_ennemis, self.bonus_fuite)


_cache = {}


def obtenir(id_classe):
    if id_classe not in _cache:
        _cache[id_classe] = importlib.import_module(f"classe.{id_classe}").CLASSE
    return _cache[id_classe]
