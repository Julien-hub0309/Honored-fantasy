"""Système de loot et de rareté (cahier §5.2).

- Raretés 1-3 (Commun, Peu commun, Rare) : au sol sur la carte. Le taux d'apparition augmente avec les combats gagnés.
- Raretés 4-6 (Très rare, Épique, Légendaire) : exclusives aux coffres et aux Boss.
"""
import random

from exploration.objets import CONSOS, depuis_id, fabriquer_arme, fabriquer_talisman, fabriquer_rune
from classe import JOUABLES

STATS_TALISMAN = ["FOR", "RES", "INT", "DEX", "AGI", "PV", "Mana"]
CONSO_PAR_RARETE = {0: ["potion_vie", "potion_mana"], 1: ["elixir_courage", "elixir_reflexion", "potion_vie", "potion_mana"],
                    2: ["potion_vie_plus", "potion_mana_plus", "elixir_courage", "elixir_reflexion"]}


class LootSystem:
    def __init__(self, rng=None):
        self.rng = rng or random.Random()

    def objet(self, rarete, classes=None):
        """Génère un objet de la rareté donnée (consommable, arme adaptée à l'équipe ou talisman)."""
        rng = self.rng
        classes = [c for c in (classes or JOUABLES) if c != "monstre"] or JOUABLES
        p_conso = 0.55 if rarete <= 2 else 0.18
        r = rng.random()
        if r < p_conso:
            ids = CONSO_PAR_RARETE.get(min(rarete, 2))
            o = depuis_id(rng.choice(ids))
            if rarete >= 3:
                o = depuis_id(rng.choice(["potion_vie_plus", "potion_mana_plus", "queue_phenix"]))
            return o
        if r < p_conso + (1 - p_conso) * 0.5:
            return fabriquer_arme(rng.choice(classes), rarete)
        return fabriquer_talisman(rng.choice(STATS_TALISMAN), rarete)

    def rarete_sol(self, poids, victoires):
        """Plus l'équipe remporte de combats, plus les raretés élevées (au sol) deviennent probables."""
        bonus = min(0.25, victoires * 0.01)
        p = [poids[0] * (1 - bonus), poids[1], poids[2] * (1 + bonus * 4)]
        return self.rng.choices([0, 1, 2], p)[0]

    def nombre_sol(self, base, victoires):
        return base + min(5, victoires // 3)

    def butin_coffre(self, bornes, classes=None):
        r = self.rng.randint(bornes[0], bornes[1])
        out = [self.objet(r, classes)]
        if self.rng.random() < 0.7:
            out.append(depuis_id(self.rng.choice(["potion_vie", "potion_mana", "potion_vie_plus"])))
        if self.rng.random() < 0.10:
            out.append(depuis_id("queue_phenix"))
        return out, self.rng.randint(25, 60) * (1 + r)

    def butin_boss(self, num, bornes, classes=None):
        out = [fabriquer_rune(num - 1), self.objet(self.rng.randint(*bornes), classes), self.objet(bornes[1], classes)]
        if self.rng.random() < 0.6:
            out.append(depuis_id("queue_phenix"))
        return out

    def butin_ennemi(self, ennemis, classes=None):
        """Petit butin aléatoire sur les ennemis (potions, parfois du matériel commun)."""
        out = []
        for e in ennemis:
            if e.boss:
                continue
            if self.rng.random() < 0.22:
                out.append(self.objet(0 if self.rng.random() < 0.8 else 1, classes))
        return out
