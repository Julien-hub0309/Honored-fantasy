"""Jauge de Mana (huile de baleine raffinée)."""
from combat.pv import Jauge


class Mana(Jauge):
    def peut_payer(self, cout):
        return self.valeur >= cout

    def payer(self, cout):
        if not self.peut_payer(cout):
            return False
        self.valeur -= cout
        return True
