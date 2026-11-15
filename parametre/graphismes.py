"""Fenêtre, résolution interne pixel-art (480x270), mise à l'échelle, plein écran, FPS, post-traitement."""
import pygame

LARGEUR, HAUTEUR = 480, 270
TUILE = 16


class Ecran:
    def __init__(self, conf):
        self.conf = conf["graphismes"]
        self.fenetre = None
        self.dest = pygame.Rect(0, 0, LARGEUR, HAUTEUR)
        self.horloge = pygame.time.Clock()
        self._scan = None
        self.creer_fenetre()
        self.surface = pygame.Surface((LARGEUR, HAUTEUR)).convert()

    def creer_fenetre(self):
        e = max(1, int(self.conf.get("echelle", 2)))
        if self.conf.get("plein_ecran"):
            self.fenetre = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.SCALED)
        else:
            self.fenetre = pygame.display.set_mode((LARGEUR * e, HAUTEUR * e), pygame.RESIZABLE)
        pygame.display.set_caption("Honored Fantasy")
        self._scan = None

    def basculer_plein_ecran(self):
        self.conf["plein_ecran"] = not self.conf.get("plein_ecran")
        self.creer_fenetre()

    def vers_interne(self, pos):
        if self.dest.w == 0:
            return pos
        return ((pos[0] - self.dest.x) * LARGEUR // self.dest.w, (pos[1] - self.dest.y) * HAUTEUR // self.dest.h)

    def _scanlines(self, taille):
        if self._scan is None or self._scan.get_size() != taille:
            s = pygame.Surface(taille, pygame.SRCALPHA)
            for y in range(0, taille[1], 2):
                pygame.draw.line(s, (0, 0, 0, 38), (0, y), (taille[0], y))
            self._scan = s
        return self._scan

    def presenter(self):
        w, h = self.fenetre.get_size()
        k = min(w / LARGEUR, h / HAUTEUR)
        k = max(1, int(k)) if k >= 1 else k
        tw, th = int(LARGEUR * k), int(HAUTEUR * k)
        self.dest = pygame.Rect((w - tw) // 2, (h - th) // 2, tw, th)
        self.fenetre.fill((0, 0, 0))
        pygame.transform.scale(self.surface, (tw, th), self.fenetre.subsurface(self.dest))
        if self.conf.get("scanlines"):
            self.fenetre.blit(self._scanlines((tw, th)), self.dest.topleft)
        pygame.display.flip()

    def tick(self):
        fps = int(self.conf.get("fps_max", 60)) or 0
        return self.horloge.tick(fps) / 1000.0
