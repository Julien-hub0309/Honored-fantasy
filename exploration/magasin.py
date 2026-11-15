"""Magasin : prix indexés sur la prospérité de la ville (plus riche = plus cher, mais raretés plus hautes)."""
import random

from exploration.loot_systeme import LootSystem
from exploration.objets import CONSOS, depuis_id
from exploration.revente import prix_revente


class Magasin:
    def __init__(self, zone, graine=0, classes=None):
        self.zone = zone
        self.prosperite = max(1, min(4, zone.prosperite))
        self.multiplicateur = 1.0 + 0.35 * (self.prosperite - 1)       # prospérité 1 -> x1.0 ; 4 -> x2.05
        rng = random.Random(f"magasin:{zone.cle}:{graine}")
        loot = LootSystem(rng)
        self.stock = []
        base = ["potion_vie", "potion_mana", "elixir_courage", "elixir_reflexion"]
        if self.prosperite >= 2:
            base += ["potion_vie_plus", "potion_mana_plus"]
        if self.prosperite >= 3 or (self.prosperite == 2 and rng.random() < 0.4):
            base.append("queue_phenix")
        for id_ in base:
            self.stock.append(self._etiqueter(depuis_id(id_)))
        rmin = min(5, self.prosperite - 1 + (1 if self.prosperite >= 3 else 0))
        rmax = min(5, self.prosperite + 1)
        for _ in range(6 if self.prosperite < 3 else 8):
            o = loot.objet(rng.randint(rmin, rmax), classes)
            if o.type != "conso":
                self.stock.append(self._etiqueter(o))
        self.stock.sort(key=lambda o: (o.type != "conso", o.rarete, o.prix))

    def _etiqueter(self, o):
        o.prix = int(o.valeur * self.multiplicateur)
        return o

    def acheter(self, etat, o):
        """Retourne True si l'achat est réalisé. La valeur d'achat devient le prix payé (base de la revente à 80 %)."""
        if etat.or_ < o.prix:
            return False
        etat.or_ -= o.prix
        c = o.copie(valeur=o.prix)
        etat.sac.ajouter(c)
        return True

    def vendre(self, etat, o):
        gain = prix_revente(o)
        if gain <= 0:
            return 0
        if etat.sac.retirer(o):
            etat.or_ += gain
            return gain
        return 0
