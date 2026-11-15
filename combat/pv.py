"""Jauge générique et jauge de Points de Vie."""


class Jauge:
    def __init__(self, maximum, valeur=None):
        self.maximum = max(0, int(maximum))
        self.valeur = self.maximum if valeur is None else max(0, min(self.maximum, int(valeur)))

    @property
    def ratio(self):
        return self.valeur / self.maximum if self.maximum else 0.0

    @property
    def vide(self):
        return self.valeur <= 0

    def perdre(self, n):
        reel = min(self.valeur, max(0, int(n)))
        self.valeur -= reel
        return reel

    def gagner(self, n):
        reel = min(self.maximum - self.valeur, max(0, int(n)))
        self.valeur += reel
        return reel

    def definir_max(self, maximum, garder_ratio=False):
        r = self.ratio
        self.maximum = max(0, int(maximum))
        self.valeur = int(self.maximum * r) if garder_ratio else min(self.valeur, self.maximum)


class Pv(Jauge):
    """Points de Vie : 0 PV = KO."""

    @property
    def ko(self):
        return self.vide
