"""Interface (HUD) façon Final Fantasy : fenêtres dégradées bleu nuit à liseré laiton (touche Dishonored).

Ce module ne contient aucune logique métier : uniquement du rendu et des widgets réutilisables.
"""
import pygame

BLANC = (240, 236, 224)
GRIS = (150, 150, 160)
OR = (232, 196, 110)
ROUGE = (240, 90, 80)
VERT = (110, 224, 120)
BLEU = (110, 170, 255)
VIOLET = (190, 130, 255)
JAUNE = (250, 220, 90)
LAITON = (201, 160, 90)

_polices = {}


def police(taille=16):
    if taille not in _polices:
        _polices[taille] = pygame.font.Font(None, taille)
    return _polices[taille]


def texte(surf, txt, pos, couleur=BLANC, taille=16, ombre=True, centre=False, droite=False):
    f = police(taille)
    img = f.render(str(txt), False, couleur)
    x, y = pos
    if centre:
        x -= img.get_width() // 2
    elif droite:
        x -= img.get_width()
    if ombre:
        noir = f.render(str(txt), False, (10, 8, 14))
        if taille >= 20:       # gros textes : contour complet
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (1, -1), (-1, 1)):
                surf.blit(noir, (x + dx, y + dy))
            surf.blit(noir, (x, y + 2))
        else:
            surf.blit(noir, (x + 1, y + 1))
    surf.blit(img, (x, y))
    return img.get_width()


def texte_degrade(surf, txt, pos, taille, haut, bas, centre=True):
    """Texte à dégradé vertical avec contour (logos, titres)."""
    f = police(taille)
    img = f.render(str(txt), False, (255, 255, 255))
    w, h = img.get_size()
    g = pygame.Surface((w, h))
    for yy in range(h):
        t = yy / max(1, h - 1)
        pygame.draw.line(g, tuple(int(haut[i] + (bas[i] - haut[i]) * t) for i in range(3)), (0, yy), (w, yy))
    img = img.convert_alpha()
    img.blit(g, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    x, y = pos
    if centre:
        x -= w // 2
    noir = f.render(str(txt), False, (14, 8, 20))
    for dx in (-2, -1, 0, 1, 2):
        for dy in (-2, -1, 0, 1, 2, 3):
            if dx or dy:
                surf.blit(noir, (x + dx, y + dy))
    surf.blit(img, (x, y))


def largeur_texte(txt, taille=16):
    return police(taille).size(str(txt))[0]


def texte_multiligne(surf, txt, rect, couleur=BLANC, taille=16, interligne=2):
    """Écrit un texte avec retours à la ligne automatiques dans rect. Retourne le nombre de lignes."""
    f = police(taille)
    x, y = rect.x, rect.y
    lignes = []
    for para in str(txt).split("\n"):
        mots, ligne = para.split(" "), ""
        for m in mots:
            essai = (ligne + " " + m).strip()
            if f.size(essai)[0] > rect.w and ligne:
                lignes.append(ligne); ligne = m
            else:
                ligne = essai
        lignes.append(ligne)
    for l in lignes:
        texte(surf, l, (x, y), couleur, taille)
        y += f.get_linesize() + interligne - 3
    return len(lignes)


def lignes_decoupees(txt, largeur, taille=16):
    f = police(taille)
    sortie = []
    for para in str(txt).split("\n"):
        ligne = ""
        for m in para.split(" "):
            essai = (ligne + " " + m).strip()
            if f.size(essai)[0] > largeur and ligne:
                sortie.append(ligne); ligne = m
            else:
                ligne = essai
        sortie.append(ligne)
    return sortie


_cache_fenetres = {}


def fenetre(surf, rect, alpha=238, bordure=LAITON, teinte=None):
    rect = pygame.Rect(rect)
    cle = (rect.w, rect.h, alpha, bordure, teinte)
    img = _cache_fenetres.get(cle)
    if img is None:
        img = pygame.Surface(rect.size, pygame.SRCALPHA)
        haut, bas = teinte or ((30, 52, 98), (9, 18, 44))
        for y in range(rect.h):
            t = y / max(1, rect.h - 1)
            c = tuple(int(haut[i] + (bas[i] - haut[i]) * t) for i in range(3)) + (alpha,)
            pygame.draw.line(img, c, (1, y), (rect.w - 2, y))
        pygame.draw.rect(img, (12, 8, 14), (0, 0, rect.w, rect.h), 1, border_radius=3)
        pygame.draw.rect(img, bordure, (1, 1, rect.w - 2, rect.h - 2), 1, border_radius=2)
        pygame.draw.rect(img, tuple(int(v * 0.45) for v in bordure), (2, 2, rect.w - 4, rect.h - 4), 1)
        pygame.draw.line(img, (255, 255, 255, 38), (4, 3), (rect.w - 5, 3))          # reflet supérieur
        pygame.draw.line(img, (0, 0, 0, 70), (4, rect.h - 4), (rect.w - 5, rect.h - 4))
        for cx, cy in ((2, 2), (rect.w - 3, 2), (2, rect.h - 3), (rect.w - 3, rect.h - 3)):
            img.set_at((cx, cy), (255, 240, 200))
        _cache_fenetres[cle] = img
    surf.blit(img, rect.topleft)


def titre(surf, txt, y, couleur=OR, taille=30):
    texte(surf, txt, (surf.get_width() // 2, y), couleur, taille, centre=True)
    larg = largeur_texte(txt, taille)
    cx = surf.get_width() // 2
    pygame.draw.line(surf, LAITON, (cx - larg // 2 - 12, y + taille - 4), (cx + larg // 2 + 12, y + taille - 4))


def barre(surf, rect, ratio, couleur, fond=(20, 16, 28), brillance=True):
    rect = pygame.Rect(rect)
    ratio = max(0.0, min(1.0, ratio))
    pygame.draw.rect(surf, (8, 6, 12), rect.inflate(2, 2))
    pygame.draw.rect(surf, fond, rect)
    w = int(rect.w * ratio)
    if w > 0:
        pygame.draw.rect(surf, couleur, (rect.x, rect.y, w, rect.h))
        if brillance and rect.h >= 3:
            pygame.draw.rect(surf, tuple(min(255, c + 70) for c in couleur), (rect.x, rect.y, w, 1))


def couleur_pv(ratio):
    return VERT if ratio > 0.5 else (JAUNE if ratio > 0.25 else ROUGE)


class Menu:
    """Menu vertical à curseur (clavier + souris), avec défilement."""

    def __init__(self, items, largeur=120, visibles=8, taille=16, desactives=None, hauteur_ligne=15):
        self.items = list(items)
        self.largeur = largeur
        self.visibles = visibles
        self.taille = taille
        self.curseur = 0
        self.debut = 0
        self.desactives = set(desactives or [])
        self.h = hauteur_ligne
        self.rects = []
        self.son = None

    def traiter(self, action, souris=None, event=None):
        n = len(self.items)
        if n == 0:
            return None
        if action == "haut":
            self.curseur = (self.curseur - 1) % n
        elif action == "bas":
            self.curseur = (self.curseur + 1) % n
        elif action == "valider":
            if self.curseur not in self.desactives:
                return self.curseur
        if souris is not None and event is not None:
            if event.type == pygame.MOUSEMOTION:
                for i, r in self.rects:
                    if r.collidepoint(souris.pos):
                        self.curseur = i
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, r in self.rects:
                    if r.collidepoint(souris.pos) and i not in self.desactives:
                        self.curseur = i
                        return i
        if self.curseur < self.debut:
            self.debut = self.curseur
        if self.curseur >= self.debut + self.visibles:
            self.debut = self.curseur - self.visibles + 1
        return None

    def dessiner(self, surf, pos, actif=True, cadre=True):
        x, y = pos
        n = min(self.visibles, len(self.items))
        if cadre:
            fenetre(surf, (x - 8, y - 6, self.largeur + 16, n * self.h + 12))
        self.rects = []
        for k in range(n):
            i = self.debut + k
            if i >= len(self.items):
                break
            it = self.items[i]
            r = pygame.Rect(x, y + k * self.h, self.largeur, self.h)
            self.rects.append((i, r))
            off = i in self.desactives
            sel = i == self.curseur and actif
            if sel:
                pygame.draw.rect(surf, (60, 90, 160), r.inflate(6, 0))
                pygame.draw.rect(surf, LAITON, r.inflate(6, 0), 1)
                curseur_main(surf, (x - 4, r.y + 2))
            texte(surf, it, (x + 8, r.y + 1), GRIS if off else (OR if sel else BLANC), self.taille)
        if len(self.items) > self.visibles:
            if self.debut > 0:
                texte(surf, "^", (x + self.largeur - 4, y - 6), OR)
            if self.debut + self.visibles < len(self.items):
                texte(surf, "v", (x + self.largeur - 4, y + n * self.h - 6), OR)


def curseur_main(surf, pos):
    x, y = pos
    pygame.draw.polygon(surf, (10, 8, 14), [(x - 1, y - 1), (x + 7, y + 4), (x - 1, y + 9)])
    pygame.draw.polygon(surf, OR, [(x, y), (x + 5, y + 4), (x, y + 8)])


class Dialogue:
    """Boîte de dialogue à effet machine à écrire. lignes = [(orateur, texte), ...]"""

    def __init__(self, lignes, couleur_nom=OR):
        self.lignes = list(lignes)
        self.i = 0
        self.t = 0.0
        self.couleur_nom = couleur_nom
        self.fini = False

    @property
    def courant(self):
        return self.lignes[self.i]

    def update(self, dt):
        self.t += dt * 55

    def valider(self):
        """Retourne True si le dialogue est terminé."""
        total = len(self.courant[1])
        if self.t < total:
            self.t = total
            return False
        self.i += 1
        self.t = 0
        if self.i >= len(self.lignes):
            self.fini = True
        return self.fini

    def dessiner(self, surf):
        if self.fini:
            return
        W, H = surf.get_size()
        r = pygame.Rect(16, H - 78, W - 32, 66)
        fenetre(surf, r)
        nom, txt = self.courant
        if nom:
            fenetre(surf, (r.x + 8, r.y - 11, largeur_texte(nom, 16) + 16, 18))
            texte(surf, nom, (r.x + 16, r.y - 8), self.couleur_nom)
        n = int(self.t)
        texte_multiligne(surf, txt[:n], pygame.Rect(r.x + 12, r.y + 10, r.w - 24, r.h - 14))
        if n >= len(txt) and int(self.t * 3) % 2 == 0:
            pygame.draw.polygon(surf, OR, [(r.right - 18, r.bottom - 12), (r.right - 10, r.bottom - 12), (r.right - 14, r.bottom - 6)])


class Flottants:
    """Textes flottants (dégâts, soins, états)."""

    def __init__(self):
        self.liste = []

    def ajouter(self, txt, pos, couleur=BLANC, taille=22, duree=0.9, rebond=True):
        self.liste.append(dict(txt=txt, x=pos[0], y=pos[1], t=0.0, c=couleur, taille=taille, d=duree, rebond=rebond))

    def update(self, dt):
        for f in self.liste:
            f["t"] += dt
        self.liste = [f for f in self.liste if f["t"] < f["d"]]

    def dessiner(self, surf):
        for f in self.liste:
            f["taille"] = max(f["taille"], 20) if f["txt"].lstrip("CRITIQUE ").isdigit() or f["txt"].startswith("CRIT") else f["taille"]
            t = f["t"] / f["d"]
            dy = -22 * min(1, t * 2.5) + (6 * (t ** 2) if f["rebond"] else 0)
            if f["rebond"] and t < 0.25:
                dy = -26 * (t / 0.25) * (1 - (t / 0.25) * 0.5)
            texte(surf, f["txt"], (f["x"], f["y"] + dy), f["c"], f["taille"], centre=True)


class Notification:
    def __init__(self):
        self.file = []

    def ajouter(self, txt, couleur=OR, duree=2.4):
        self.file.append([txt, couleur, duree])

    def update(self, dt):
        if self.file:
            self.file[0][2] -= dt
            if self.file[0][2] <= 0:
                self.file.pop(0)

    def dessiner(self, surf):
        if not self.file:
            return
        txt, c, d = self.file[0]
        w = largeur_texte(txt, 16) + 20
        y = 8 - max(0, int((0.25 - d) * -40)) if d < 0.25 else 8
        fenetre(surf, ((surf.get_width() - w) // 2, y, w, 20))
        texte(surf, txt, (surf.get_width() // 2, y + 4), c, centre=True)


def etiquette_rarete(surf, pos, rarete, taille=16):
    from assets import pixelart as px
    texte(surf, px.RARETE_NOMS[rarete], pos, px.RARETE_COULEURS[rarete], taille)
