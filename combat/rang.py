"""Altérations d'état (buffs / débuffs) : le « rang » de chaque statistique."""
from dataclasses import dataclass, field


@dataclass
class Alteration:
    id: str
    nom: str
    duree: int
    ajout: dict = field(default_factory=dict)   # {"FOR": +2}
    fixe: dict = field(default_factory=dict)    # {"AGI": 0}  (force la valeur)
    positif: bool = True
    dot: int = 0                                # dégâts bruts infligés à la fin de chaque tour du porteur


class Rang:
    def __init__(self):
        self.liste = []

    def ajouter(self, alt):
        self.liste = [a for a in self.liste if a.id != alt.id]   # rafraîchit si déjà présente
        self.liste.append(alt)

    def a(self, id_):
        return any(a.id == id_ for a in self.liste)

    def retirer(self, id_):
        self.liste = [a for a in self.liste if a.id != id_]

    def appliquer(self, stat, base):
        v = base
        for a in self.liste:
            v += a.ajout.get(stat, 0)
        for a in self.liste:
            if stat in a.fixe:
                v = a.fixe[stat]
        return max(0, v)

    def malus(self):
        """Vrai si le porteur subit au moins une altération négative."""
        return any(not a.positif for a in self.liste)

    def tick(self):
        """Fin de tour du porteur. Retourne les altérations expirées."""
        expirees = []
        for a in self.liste:
            a.duree -= 1
            if a.duree <= 0:
                expirees.append(a)
        self.liste = [a for a in self.liste if a.duree > 0]
        return expirees

    def vider(self):
        self.liste = []
