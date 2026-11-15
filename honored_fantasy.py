#!/usr/bin/env python3
"""Honored Fantasy - point d'entrée et boucle principale.

RPG tactique au tour par tour, exploration 2D, pixel art chibi (Dishonored x Final Fantasy).
Lancement :  python honored_fantasy.py
"""
import os
import sys

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import pygame
except ImportError:
    sys.exit("Pygame est absent. Lancez d'abord :  python installateur.py")

from assets.audio import Audio
from HUD import hud
from HUD.ecrans import SceneTitre
from parametre import config
from parametre.clavier import Clavier
from parametre.graphismes import Ecran
from parametre.souris import Souris


class Jeu:
    """Contexte partagé par toutes les scènes + pile de scènes (la scène du dessus est active)."""

    def __init__(self):
        pygame.init()
        self.conf = config.charger()
        self.ecran = Ecran(self.conf)
        self.clavier = Clavier(self.conf)
        self.souris = Souris(self.ecran)
        self.audio = Audio(self.conf)
        self.notif = hud.Notification()
        self.etat = None
        self.scenes = []
        self.quitter = False

    def notif_couleur(self, rarete):
        from assets import pixelart as px
        return px.RARETE_COULEURS[rarete]

    # ---- pile de scènes
    def pousser(self, scene):
        self.scenes.append(scene)

    def retour(self):
        self.scenes.pop()
        if self.scenes and hasattr(self.scenes[-1], "reprendre"):
            self.scenes[-1].reprendre(self)

    def changer(self, scene):
        self.scenes[-1] = scene

    def reinitialiser(self, scene):
        self.scenes = [scene]

    # ---- boucle
    def boucle(self):
        while not self.quitter and self.scenes:
            dt = min(0.05, self.ecran.tick())
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quitter = True
                    continue
                if event.type == pygame.KEYDOWN and self.clavier.action(event) == "plein_ecran":
                    self.ecran.basculer_plein_ecran()
                    config.sauvegarder(self.conf)
                    continue
                self.souris.traiter(event)
                if self.scenes:
                    self.scenes[-1].handle(event, self)
            if not self.scenes:
                break
            scene = self.scenes[-1]
            scene.update(dt, self)
            self.notif.update(dt)
            scene = self.scenes[-1]
            scene.draw(self.ecran.surface, self)
            self.notif.dessiner(self.ecran.surface)
            self.ecran.presenter()
            self.souris.fin_image()
        config.sauvegarder(self.conf)
        pygame.quit()


def main():
    jeu = Jeu()
    jeu.pousser(SceneTitre(jeu))
    jeu.boucle()


if __name__ == "__main__":
    main()
