"""Mapping des touches : transforme les touches pygame en actions logiques (AZERTY/QWERTY)."""
import pygame


class Clavier:
    def __init__(self, conf):
        self.conf = conf
        self.recharger()

    def recharger(self):
        self.table = {}
        for action, noms in self.conf["touches"].items():
            for nom in noms:
                try:
                    self.table[pygame.key.key_code(nom)] = action
                except ValueError:
                    pass

    def action(self, event):
        """Retourne l'action logique associée à un KEYDOWN (ou None)."""
        if event.type == pygame.KEYDOWN:
            return self.table.get(event.key)
        return None

    def maintenu(self, action):
        touches = pygame.key.get_pressed()
        for nom in self.conf["touches"].get(action, []):
            try:
                if touches[pygame.key.key_code(nom)]:
                    return True
            except ValueError:
                pass
        return False

    def direction(self):
        dx = int(self.maintenu("droite")) - int(self.maintenu("gauche"))
        dy = int(self.maintenu("bas")) - int(self.maintenu("haut"))
        return dx, dy
