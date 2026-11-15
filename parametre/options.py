"""Menu des options (scène réutilisable depuis le titre et le menu pause)."""
import pygame
from HUD import hud
from parametre import config


class SceneOptions:
    def __init__(self, jeu):
        self.jeu = jeu
        self.menu = hud.Menu(self._libelles(), largeur=210)
        self.menu.curseur = 0

    def _libelles(self):
        g = self.jeu.conf["graphismes"]
        a = self.jeu.conf["audio"]
        oui = lambda v: "Oui" if v else "Non"
        return [
            f"Plein écran : {oui(g['plein_ecran'])}",
            f"Taille fenêtre : x{g['echelle']}",
            f"Ambiance lumineuse : {oui(g['ambiance'])}",
            f"Lignes CRT : {oui(g['scanlines'])}",
            f"FPS max : {g['fps_max'] or 'illimité'}",
            f"Volume : {int(a['volume'] * 100)}%",
            "Retour",
        ]

    def handle(self, event, jeu):
        act = jeu.clavier.action(event)
        if act == "annuler":
            return self._sortir()
        choix = self.menu.traiter(act, jeu.souris, event)
        if choix is None:
            return
        g, a = jeu.conf["graphismes"], jeu.conf["audio"]
        if choix == 0:
            jeu.ecran.basculer_plein_ecran()
        elif choix == 1:
            g["echelle"] = g["echelle"] % 4 + 1
            if not g["plein_ecran"]:
                jeu.ecran.creer_fenetre()
        elif choix == 2:
            g["ambiance"] = not g["ambiance"]
        elif choix == 3:
            g["scanlines"] = not g["scanlines"]
        elif choix == 4:
            suite = [30, 60, 120, 0]
            g["fps_max"] = suite[(suite.index(g["fps_max"]) + 1) % 4] if g["fps_max"] in suite else 60
        elif choix == 5:
            a["volume"] = round((a["volume"] + 0.1) % 1.1, 1)
            jeu.audio.regler(a["volume"])
        else:
            return self._sortir()
        self.menu.items = self._libelles()

    def _sortir(self):
        config.sauvegarder(self.jeu.conf)
        self.jeu.retour()

    def update(self, dt, jeu):
        pass

    def draw(self, surf, jeu):
        surf.fill((8, 10, 16))
        hud.titre(surf, "OPTIONS", 28)
        self.menu.dessiner(surf, (135, 70))
