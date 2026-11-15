"""Gestion de la souris : position convertie en coordonnées internes, clics et survols."""
import pygame


class Souris:
    def __init__(self, ecran):
        self.ecran = ecran
        self.pos = (0, 0)
        self.clic = False
        self.bouge = False

    def traiter(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.pos = self.ecran.vers_interne(event.pos)
            self.bouge = True
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.pos = self.ecran.vers_interne(event.pos)
            self.clic = True

    def fin_image(self):
        self.clic = False
        self.bouge = False

    def survole(self, rect):
        return rect.collidepoint(self.pos)
