"""Générateur de pixel art : tuiles par biome, sprites chibi, monstres, boss, icônes, décors de combat.

Direction artistique : gothique industriel (Dishonored : ville baleinière, brume, huile de baleine)
croisé avec le cristal et le chibi de Final Fantasy. Palettes imposées par le cahier des charges.
"""
import math
import random
import zlib
import pygame

SA = pygame.SRCALPHA


def hexc(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def surf(w, h):
    return pygame.Surface((w, h), SA)


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def sombre(c, t=0.3):
    return mix(c, (0, 0, 0), t)


def clair(c, t=0.3):
    return mix(c, (255, 255, 255), t)


CONTOUR = hexc("#120e16")

# --------------------------------------------------------------------------------------
# Palettes par biome (cahier des charges §6)
# --------------------------------------------------------------------------------------
PALETTES = {
    # Villes : propre, lumineux. Jaune / Orange / Rouge
    "ville": dict(sol1=hexc("#d8b668"), sol2=hexc("#b8924a"), sol3=hexc("#efd48c"), mur1=hexc("#c8582c"), mur2=hexc("#8e3220"),
                  toit1=hexc("#b02e28"), toit2=hexc("#7c1e22"), herbe1=hexc("#7aa84a"), herbe2=hexc("#58863a"), tronc=hexc("#6a4426"),
                  eau=hexc("#4f9fb8"), eau2=hexc("#86cde0"), accent=hexc("#f0a030"), lumiere=hexc("#ffd878"), ombre=hexc("#4a2a22"),
                  metal=hexc("#6e7480"), bois=hexc("#8a5a30")),
    # Forêts : Jaune / Vert clair / Vert foncé / Gris
    "foret": dict(sol1=hexc("#6fa84a"), sol2=hexc("#5a9040"), sol3=hexc("#92c262"), mur1=hexc("#2e4a2a"), mur2=hexc("#1c3320"),
                  toit1=hexc("#2e4a2a"), toit2=hexc("#1c3320"), herbe1=hexc("#3f7a34"), herbe2=hexc("#25502a"), tronc=hexc("#6b6a62"),
                  eau=hexc("#587a78"), eau2=hexc("#8fb0a8"), accent=hexc("#e8d040"), lumiere=hexc("#f0e080"), ombre=hexc("#14281a"),
                  metal=hexc("#8a8e88"), bois=hexc("#5a4a30")),
    # Donjons : Vert foncé / Marron / Gris / Noir
    "donjon": dict(sol1=hexc("#2c3a30"), sol2=hexc("#202a24"), sol3=hexc("#3c4c3e"), mur1=hexc("#4a4a44"), mur2=hexc("#22221f"),
                   toit1=hexc("#22221f"), toit2=hexc("#121210"), herbe1=hexc("#2a4a2c"), herbe2=hexc("#1a301c"), tronc=hexc("#5a3e26"),
                   eau=hexc("#1c3a34"), eau2=hexc("#2e6058"), accent=hexc("#f08a30"), lumiere=hexc("#ffb050"), ombre=hexc("#080a08"),
                   metal=hexc("#76766e"), bois=hexc("#6a4a2a")),
    # Void : Bleu / Violet / Gris / Noir
    "void": dict(sol1=hexc("#1c2250"), sol2=hexc("#141840"), sol3=hexc("#2c3470"), mur1=hexc("#2a1a50"), mur2=hexc("#120a2a"),
                 toit1=hexc("#3a2478"), toit2=hexc("#1c1040"), herbe1=hexc("#4a3a9a"), herbe2=hexc("#2a2070"), tronc=hexc("#5a5a78"),
                 eau=hexc("#0a0c2a"), eau2=hexc("#4a54c0"), accent=hexc("#9a60ff"), lumiere=hexc("#80a0ff"), ombre=hexc("#04030c"),
                 metal=hexc("#7a7a98"), bois=hexc("#4a3a6a")),
    # Plaines / falaises du Realme : herbe sèche, gris, jaune
    "ouvert": dict(sol1=hexc("#9aa060"), sol2=hexc("#80883e"), sol3=hexc("#b8bc78"), mur1=hexc("#7a7a74"), mur2=hexc("#46463f"),
                   toit1=hexc("#7a7a74"), toit2=hexc("#46463f"), herbe1=hexc("#6f8a40"), herbe2=hexc("#4a6a30"), tronc=hexc("#6e6a5c"),
                   eau=hexc("#3f6e8c"), eau2=hexc("#7eb0c8"), accent=hexc("#e8c850"), lumiere=hexc("#ffe8a0"), ombre=hexc("#2a2a24"),
                   metal=hexc("#8a8c88"), bois=hexc("#6a5030")),
}


def jitter(c, rng, amt=0.08):
    k = 1 + rng.uniform(-amt, amt)
    return tuple(max(0, min(255, int(v * k))) for v in c)


def ombrer(img):
    """Ombrage automatique d'un sprite (lumière en haut à gauche) : liseré clair sur les bords hauts/gauches,
    arêtes sombres en bas/à droite, léger dégradé vertical. Donne du volume aux aplats."""
    w, h = img.get_size()
    out = img.copy()
    src = [[img.get_at((x, y)) for x in range(w)] for y in range(h)]

    def vide(x, y):
        return not (0 <= x < w and 0 <= y < h) or src[y][x][3] < 40

    for y in range(h):
        for x in range(w):
            r, g, b, a = src[y][x]
            if a < 40:
                continue
            t = 0.0
            if vide(x, y - 1):
                t += 0.22
            if vide(x - 1, y):
                t += 0.12
            if vide(x, y + 1):
                t -= 0.28
            if vide(x + 1, y):
                t -= 0.18
            t -= 0.10 * (y / h) - 0.04
            if t > 0:
                c = (int(r + (255 - r) * t), int(g + (255 - g) * t), int(b + (255 - b) * t), a)
            else:
                k = 1 + t
                c = (int(r * k), int(g * k * 0.99), int(b * k * 1.02 if b * k * 1.02 < 255 else 255), a)
            out.set_at((x, y), c)
    return out


def _speckle(s, rng, couleurs, n, rect=None):
    w, h = s.get_size()
    for _ in range(n):
        x, y = rng.randrange(w), rng.randrange(h)
        s.set_at((x, y), rng.choice(couleurs))


# --------------------------------------------------------------------------------------
# Tuiles 16x16
# --------------------------------------------------------------------------------------
def _sol(kind, p, rng, frame):
    s = pygame.Surface((16, 16))
    if kind == "pave":
        s.fill(p["sol2"])
        for r, y in enumerate((0, 5, 10)):
            off = 0 if r % 2 == 0 else 4
            for x in range(-off, 16, 8):
                c = jitter(p["sol1"], rng, 0.07)
                pygame.draw.rect(s, c, (x + 1, y + 1, 7, 4))
                pygame.draw.line(s, clair(c, 0.22), (x + 1, y + 1), (x + 7, y + 1))
                pygame.draw.line(s, sombre(c, 0.18), (x + 1, y + 4), (x + 7, y + 4))
        _speckle(s, rng, [p["sol3"], sombre(p["sol1"], 0.15)], 10)
        for _ in range(2):
            s.set_at((rng.randrange(16), rng.choice((0, 5, 10))), p["herbe1"])
    elif kind == "terre":
        s.fill(p["sol1"])
        _speckle(s, rng, [p["sol2"], p["sol3"], p["sol2"]], 30)
        for _ in range(3):
            x, y = rng.randrange(1, 14), rng.randrange(1, 14)
            pygame.draw.rect(s, p["sol3"], (x, y, 2, 1)); pygame.draw.rect(s, p["sol2"], (x, y + 1, 2, 1))
    elif kind == "herbe":
        s.fill(jitter(p["sol1"], rng, 0.04))
        _speckle(s, rng, [p["sol2"], p["sol3"], p["sol2"]], 24)
        for _ in range(5):
            x, y = rng.randrange(1, 15), rng.randrange(2, 15)
            s.set_at((x, y), p["herbe2"]); s.set_at((x, y - 1), p["herbe1"]); s.set_at((x + 1, y - 1), p["sol3"])
        if rng.random() < 0.18:
            x, y = rng.randrange(2, 14), rng.randrange(2, 14)
            fleur = rng.choice([p["accent"], (240, 240, 235), p["lumiere"]])
            s.set_at((x, y), fleur); s.set_at((x + 1, y), fleur); s.set_at((x, y + 1), p["herbe2"])
    elif kind == "dalle":
        c = jitter(p["sol1"], rng, 0.06)
        s.fill(c)
        pygame.draw.line(s, sombre(c, 0.35), (0, 15), (15, 15)); pygame.draw.line(s, sombre(c, 0.35), (15, 0), (15, 15))
        pygame.draw.line(s, clair(c, 0.2), (0, 0), (14, 0)); pygame.draw.line(s, clair(c, 0.2), (0, 0), (0, 14))
        pygame.draw.rect(s, sombre(c, 0.12), (3, 3, 10, 10), 1)
        _speckle(s, rng, [p["sol2"], p["sol3"]], 12)
        if rng.random() < 0.35:
            x = rng.randrange(3, 12); y = rng.randrange(3, 12)
            pygame.draw.line(s, sombre(c, 0.45), (x, y), (x + rng.randint(-3, 3), y + rng.randint(2, 4)))
        if rng.random() < 0.25:
            for _ in range(4):
                s.set_at((rng.randrange(1, 6), rng.randrange(1, 6)), p["herbe1"])
    elif kind == "void":
        s.fill(jitter(p["sol1"], rng, 0.1))
        pygame.draw.rect(s, p["sol2"], (0, 0, 16, 16), 1)
        pygame.draw.line(s, p["sol3"], (1, 1), (14, 1))
        for y in range(2, 16, 4):                                   # reflets verticaux : le sol est un miroir sombre
            s.set_at((rng.randrange(2, 14), y), p["sol3"])
        _speckle(s, rng, [p["sol2"], p["sol3"]], 10)
        if rng.random() < 0.4:
            x, y = rng.randrange(2, 12), rng.randrange(2, 12)
            col = p["accent"] if frame == 0 else p["lumiere"]
            for k in range(5):
                s.set_at((x + k, y + (k * 7 % 3) - 1), col)
                if k % 2 == 0:
                    s.set_at((x + k, y + (k * 7 % 3)), sombre(col, 0.5))
    elif kind == "sur":  # zone de repos : dalles claires, liseré doré
        s = _sol("pave", p, rng, frame)
        pygame.draw.rect(s, p["lumiere"], (0, 0, 16, 16), 1)
        s.set_at((0, 0), (255, 255, 255)); s.set_at((15, 15), p["accent"])
    return s


def _mur(kind, p, rng, frame):
    s = pygame.Surface((16, 16))
    if kind == "brique":
        s.fill(sombre(p["mur2"], 0.25))
        for r, y in enumerate((0, 4, 8, 12)):
            off = 0 if r % 2 == 0 else 4
            for x in range(-off, 16, 8):
                c = jitter(p["mur1"], rng, 0.09)
                pygame.draw.rect(s, c, (x + 1, y + 1, 7, 3))
                pygame.draw.line(s, clair(c, 0.2), (x + 1, y + 1), (x + 7, y + 1))
                pygame.draw.line(s, sombre(c, 0.25), (x + 1, y + 3), (x + 7, y + 3))
        pygame.draw.line(s, clair(p["mur1"], 0.35), (0, 0), (15, 0))
        pygame.draw.line(s, sombre(p["mur2"], 0.5), (0, 15), (15, 15))
        _speckle(s, rng, [p["mur2"], clair(p["mur1"], 0.15)], 6)
    elif kind == "pierre":
        s.fill(sombre(p["mur2"], 0.3))
        for y0 in (0, 8):
            cut = rng.randint(4, 11)
            for x0, x1 in ((0, cut), (cut + 1, 15)):
                c = jitter(p["mur1"], rng, 0.1)
                pygame.draw.rect(s, c, (x0, y0, x1 - x0 + 1, 7))
                pygame.draw.line(s, clair(c, 0.22), (x0, y0), (x1, y0))
                pygame.draw.line(s, sombre(c, 0.3), (x0, y0 + 6), (x1, y0 + 6))
        _speckle(s, rng, [p["herbe2"], p["mur2"], p["herbe2"], p["herbe1"]], 9)
        pygame.draw.line(s, sombre(p["mur2"], 0.6), (0, 15), (15, 15))
    elif kind == "void":
        s.fill(p["mur2"])
        pygame.draw.polygon(s, p["mur1"], [(0, 15), (5, 3), (11, 9), (15, 0), (15, 15)])
        pygame.draw.polygon(s, clair(p["mur1"], 0.12), [(5, 3), (11, 9), (8, 9), (4, 7)])
        for _ in range(2):
            x = rng.randrange(2, 14); y = rng.randrange(2, 14)
            pygame.draw.line(s, p["accent"] if frame == 0 else p["lumiere"], (x, y), (x + rng.randint(-4, 4), y + rng.randint(3, 6)))
        pygame.draw.line(s, p["sol3"], (0, 0), (15, 0))
        pygame.draw.line(s, p["ombre"], (0, 15), (15, 15))
    return s


def _toit(p, rng):
    """Toiture en tuiles : chaque tuile a sa teinte, ligne de faîte, mousse et salissures."""
    s = pygame.Surface((16, 16)); s.fill(sombre(p["toit2"], 0.3))
    for y in range(0, 16, 4):
        off = 0 if (y // 4) % 2 == 0 else 4
        for x in range(-off, 16, 8):
            c = jitter(p["toit1"], rng, 0.13)
            pygame.draw.rect(s, c, (x, y, 7, 3))
            pygame.draw.line(s, clair(c, 0.3), (x, y), (x + 6, y))
            pygame.draw.line(s, sombre(c, 0.35), (x, y + 3), (x + 7, y + 3))
    if rng.random() < 0.3:
        for _ in range(3):
            s.set_at((rng.randrange(16), rng.randrange(16)), p["herbe2"])
    if rng.random() < 0.15:
        pygame.draw.rect(s, sombre(p["toit2"], 0.5), (rng.randrange(2, 12), rng.randrange(2, 12), 3, 2))
    return s


def _facade(p, rng, porte=False, frame=0, mur="brique"):
    s = _mur(mur, p, rng, frame)
    if porte:
        pygame.draw.rect(s, p["bois"], (4, 3, 8, 13)); pygame.draw.rect(s, sombre(p["bois"], 0.4), (4, 3, 8, 13), 1)
        pygame.draw.line(s, sombre(p["bois"], 0.4), (8, 3), (8, 15)); s.set_at((10, 9), p["lumiere"])
        pygame.draw.rect(s, p["accent"], (3, 1, 10, 2))
    else:
        pygame.draw.rect(s, sombre(p["mur2"], 0.5), (4, 4, 8, 8))
        pygame.draw.rect(s, p["lumiere"] if (rng.random() < 0.7) else sombre(p["eau"], 0.2), (5, 5, 6, 6))
        pygame.draw.line(s, sombre(p["mur2"], 0.5), (8, 5), (8, 10)); pygame.draw.line(s, sombre(p["mur2"], 0.5), (5, 8), (10, 8))
    return s


def _eau(p, rng, frame):
    s = pygame.Surface((16, 16)); s.fill(p["eau"])
    for y in (3, 8, 13):
        for x in range(0, 16, 4):
            xx = (x + frame * 2 + y) % 16
            s.set_at((xx, y), p["eau2"]); s.set_at(((xx + 1) % 16, y), p["eau2"])
    return s


def _abime(p, rng, frame):
    s = pygame.Surface((16, 16)); s.fill(p["ombre"])
    for _ in range(4):
        x, y = rng.randrange(16), rng.randrange(16)
        s.set_at((x, y), p["lumiere"] if (frame + x) % 2 else p["accent"])
    return s


def _ombre_sol(s, x=2, y=11, w=12, h=5, a=80):
    o = surf(16, 16)
    pygame.draw.ellipse(o, (0, 0, 0, a), (x, y, w, h))
    s.blit(o, (0, 0))


def _arbre(p, rng, void=False):
    s = surf(16, 16)
    _ombre_sol(s, 1, 11, 14, 5, 90)
    if void:  # arbre-cristal du Void
        pygame.draw.polygon(s, p["herbe2"], [(8, 0), (13, 10), (3, 10)])
        pygame.draw.polygon(s, p["accent"], [(8, 2), (11, 9), (8, 9)])
        pygame.draw.polygon(s, p["lumiere"], [(8, 2), (8, 9), (6, 9)])
        pygame.draw.rect(s, p["tronc"], (7, 10, 2, 5))
        return s
    pygame.draw.rect(s, p["tronc"], (7, 9, 3, 7)); s.set_at((7, 12), sombre(p["tronc"], 0.4))
    for cx, cy, r, c in ((8, 6, 6, sombre(p["herbe2"], 0.25)), (5, 8, 4, sombre(p["herbe2"], 0.15)), (11, 8, 4, sombre(p["herbe2"], 0.15)),
                         (8, 6, 5, p["herbe2"]), (7, 5, 4, p["herbe1"]), (10, 4, 3, p["herbe1"]), (6, 4, 2, clair(p["herbe1"], 0.2))):
        pygame.draw.circle(s, c, (cx, cy), r)
    for _ in range(7):
        s.set_at((rng.randint(3, 12), rng.randint(2, 8)), clair(p["herbe1"], 0.4))
    for _ in range(4):
        s.set_at((rng.randint(4, 12), rng.randint(7, 10)), sombre(p["herbe2"], 0.45))
    return s


def _herbe_haute(p, rng, frame):
    s = _sol("herbe", p, rng, 0)
    for x in range(1, 16, 3):
        h = rng.randint(5, 8); dx = frame if (x // 3) % 2 else -frame
        pygame.draw.line(s, p["herbe2"], (x, 15), (x + dx, 15 - h))
        pygame.draw.line(s, p["herbe1"], (x + 1, 15), (x + 1 + dx, 14 - h))
        s.set_at((x + dx, 15 - h), p["accent"] if rng.random() < 0.25 else p["sol3"])
    return s


def _decor(kind, p, rng):
    s = surf(16, 16)
    if kind == "tonneau":
        pygame.draw.ellipse(s, p["bois"], (3, 3, 10, 12)); pygame.draw.line(s, p["metal"], (3, 6), (12, 6)); pygame.draw.line(s, p["metal"], (3, 11), (12, 11))
        pygame.draw.line(s, clair(p["bois"], 0.3), (6, 4), (6, 13))
    elif kind == "caisse":
        pygame.draw.rect(s, p["bois"], (2, 4, 12, 11)); pygame.draw.rect(s, sombre(p["bois"], 0.4), (2, 4, 12, 11), 1)
        pygame.draw.line(s, sombre(p["bois"], 0.4), (2, 4), (13, 14)); pygame.draw.line(s, sombre(p["bois"], 0.4), (13, 4), (2, 14))
    elif kind == "lampadaire":
        pygame.draw.rect(s, p["metal"], (7, 5, 2, 11)); pygame.draw.rect(s, sombre(p["metal"], 0.4), (5, 14, 6, 2))
        pygame.draw.rect(s, p["lumiere"], (5, 1, 6, 5)); pygame.draw.rect(s, p["metal"], (5, 0, 6, 1)); pygame.draw.rect(s, p["metal"], (5, 6, 6, 1))
    elif kind == "pilier":
        pygame.draw.rect(s, p["mur1"], (4, 1, 8, 15)); pygame.draw.rect(s, p["mur2"], (4, 1, 8, 15), 1)
        pygame.draw.rect(s, clair(p["mur1"], 0.25), (3, 0, 10, 2)); pygame.draw.rect(s, clair(p["mur1"], 0.25), (3, 14, 10, 2))
    elif kind == "rocher":
        pygame.draw.polygon(s, p["mur1"], [(1, 15), (3, 7), (8, 3), (13, 7), (15, 15)])
        pygame.draw.polygon(s, clair(p["mur1"], 0.25), [(3, 7), (8, 3), (9, 8), (5, 9)])
        pygame.draw.line(s, p["mur2"], (1, 15), (15, 15))
    elif kind == "buisson":
        for cx, cy, r in ((5, 10, 4), (10, 9, 5), (8, 11, 4)):
            pygame.draw.circle(s, p["herbe2"], (cx, cy), r)
        for _ in range(3):
            s.set_at((rng.randint(3, 12), rng.randint(6, 11)), p["accent"])
    elif kind == "cristal":
        pygame.draw.polygon(s, p["herbe2"], [(8, 0), (12, 12), (8, 15), (4, 12)])
        pygame.draw.polygon(s, p["accent"], [(8, 1), (11, 11), (8, 14)])
        pygame.draw.polygon(s, p["lumiere"], [(8, 1), (8, 14), (6, 11)])
    elif kind == "stalagmite":
        pygame.draw.polygon(s, p["mur1"], [(3, 15), (7, 3), (9, 3), (13, 15)])
        pygame.draw.polygon(s, p["mur2"], [(9, 3), (13, 15), (9, 15)])
    elif kind == "statue":
        pygame.draw.rect(s, p["mur2"], (3, 12, 10, 4)); pygame.draw.rect(s, p["mur1"], (5, 5, 6, 8))
        pygame.draw.circle(s, clair(p["mur1"], 0.15), (8, 4), 3); s.set_at((7, 4), p["ombre"]); s.set_at((9, 4), p["ombre"])
    elif kind == "baleine":  # enseigne / cuve d'huile de baleine
        pygame.draw.rect(s, p["metal"], (3, 4, 10, 11)); pygame.draw.rect(s, p["lumiere"], (5, 6, 6, 6)); pygame.draw.rect(s, sombre(p["metal"], 0.4), (3, 4, 10, 11), 1)
        pygame.draw.rect(s, p["accent"], (6, 7, 4, 4))
    return s


def _torche(p, rng, frame, mur):
    s = _mur(mur, p, rng, 0)
    pygame.draw.rect(s, p["bois"], (7, 7, 2, 6))
    h = 4 + (frame % 2)
    pygame.draw.polygon(s, p["accent"], [(8, 7 - h), (11, 7), (5, 7)])
    pygame.draw.polygon(s, p["lumiere"], [(8, 8 - h), (10, 7), (6, 7)])
    return s


def _sortie(p, rng, frame, vers_void=False):
    s = _sol("dalle", p, rng, 0)
    c1, c2 = (p["accent"], p["lumiere"])
    pygame.draw.rect(s, sombre(c1, 0.6), (0, 0, 16, 16))
    for r, c in ((7, c1), (5, c2), (3, clair(c2, 0.5))):
        pygame.draw.circle(s, c, (8, 8), r + (frame % 2) * (1 if r == 7 else 0), 1 if r != 3 else 0)
    return s


def _autel(p, rng, frame):
    s = _sol("dalle", p, rng, 0)
    pygame.draw.rect(s, p["mur2"], (3, 9, 10, 6)); pygame.draw.rect(s, p["mur1"], (4, 7, 8, 3))
    c = p["lumiere"] if frame % 2 else p["accent"]
    pygame.draw.polygon(s, c, [(8, 0), (11, 4), (8, 8), (5, 4)])        # la Marque de l'Outsider
    pygame.draw.polygon(s, sombre(c, 0.5), [(8, 2), (10, 4), (8, 6), (6, 4)], 1)
    s.set_at((8, 4), (255, 255, 255))
    return s


def _fontaine(p, rng, frame):
    s = _sol("pave", p, rng, 0)
    pygame.draw.ellipse(s, p["mur2"], (1, 5, 14, 11)); pygame.draw.ellipse(s, p["eau"], (3, 7, 10, 7))
    pygame.draw.rect(s, p["mur1"], (7, 1, 2, 8)); s.set_at((7 + frame % 2, 1), p["eau2"]); s.set_at((8, 0), p["eau2"])
    return s


def fabriquer_tuile(kind, pal_nom, sol="pave", mur="brique", frame=0, seed=0):
    """Fabrique une tuile 16x16 opaque. kind : voir dictionnaire interne."""
    p = PALETTES[pal_nom]
    rng = random.Random(seed * 7919 + zlib.crc32(kind.encode()) % 10007)
    void = pal_nom == "void"
    if kind in ("pave", "terre", "herbe", "dalle", "void", "sur"):
        return _sol(kind, p, rng, frame)
    if kind == "mur":
        return _mur(mur, p, rng, frame)
    if kind == "toit":
        return _toit(p, rng)
    if kind == "facade":
        return _facade(p, rng, False, frame, mur)
    if kind == "porte":
        return _facade(p, rng, True, frame, mur)
    if kind == "eau":
        return _eau(p, rng, frame)
    if kind == "abime":
        return _abime(p, rng, frame)
    if kind == "herbe_haute":
        return _herbe_haute(p, rng, frame)
    if kind == "torche":
        return _torche(p, rng, frame, mur)
    if kind == "sortie":
        return _sortie(p, rng, frame)
    if kind == "autel":
        return _autel(p, rng, frame)
    if kind == "fontaine":
        return _fontaine(p, rng, frame)
    base = _sol(sol, p, rng, 0)
    if kind == "arbre":
        base.blit(_arbre(p, rng, void), (0, 0))
    else:
        if kind not in ("lampadaire",):
            _ombre_sol(base, 2, 12, 12, 4, 70)
        base.blit(_decor(kind, p, rng), (0, 0))
    return base


ESPECES = {
    "capybara": dict(nom="Capybara", fur=hexc("#9c6a3a"), sombre=hexc("#6a4224"), clair=hexc("#efd6a8"), nez=hexc("#1c0e08"), oeil=hexc("#2a1810")),
    "panda": dict(nom="Panda", fur=hexc("#f0f0ee"), sombre=hexc("#26262c"), clair=hexc("#ffffff"), nez=hexc("#14141a"), oeil=hexc("#ffffff")),
    "renard": dict(nom="Renard", fur=hexc("#e27a2a"), sombre=hexc("#96461a"), clair=hexc("#fff0d8"), nez=hexc("#181010"), oeil=hexc("#2a1808")),
    "loup": dict(nom="Loup", fur=hexc("#7a8290"), sombre=hexc("#464c5c"), clair=hexc("#ced4de"), nez=hexc("#14141a"), oeil=hexc("#f0c846")),
}


def _oreilles(f, e, hy):
    fur, som = e["fur"], e["sombre"]
    if e["nom"] == "Capybara":
        for x in (3, 11):
            f(fur, x, hy - 2, 2, 2); f(som, x + (1 if x == 3 else 0), hy - 1, 1, 1)
    elif e["nom"] == "Panda":
        for x in (3, 10):
            f(som, x, hy - 3, 3, 3)
        f((0, 0, 0, 0), 3, hy - 3, 1, 1); f((0, 0, 0, 0), 12, hy - 3, 1, 1)
    else:   # renard / loup : oreilles pointues
        haut = 4 if e["nom"] == "Renard" else 3
        for lado in (0, 1):
            for r in range(haut):
                w = 3 - (r * 3 // haut)
                x0 = 3 if lado == 0 else 13 - max(1, w)
                f(fur, x0, hy - 1 - r, max(1, w), 1)
            f(som, 4 if lado == 0 else 11, hy - 1, 1, 1)
            f(som, 3 if lado == 0 else 12, hy - haut, 1, 1)


def _queue(f, e, top):
    n = e["nom"]
    if n == "Renard":
        f(e["fur"], 12, 18 + top, 3, 4); f(e["fur"], 13, 16 + top, 2, 3); f(e["clair"], 13, 15 + top, 2, 1); f(e["sombre"], 12, 21 + top, 3, 1)
    elif n == "Loup":
        f(e["fur"], 12, 19 + top, 2, 4); f(e["sombre"], 13, 22 + top, 1, 2)
    elif n == "Panda":
        f(e["clair"], 12, 21 + top, 2, 2)


def _visage_animal(f, e, d, hy):
    n, nez, oeil, clair, som = e["nom"], e["nez"], e["oeil"], e["clair"], e["sombre"]
    if d == "bas":
        if n == "Capybara":
            f(clair, 5, hy + 3, 6, 4); f(nez, 6, hy + 4, 1, 1); f(nez, 9, hy + 4, 1, 1); f(som, 7, hy + 6, 2, 1)
            f(oeil, 5, hy + 2, 1, 2); f(oeil, 10, hy + 2, 1, 2)
        elif n == "Panda":
            f(som, 5, hy + 3, 2, 2); f(som, 9, hy + 3, 2, 2); f(oeil, 6, hy + 3, 1, 1); f(oeil, 9, hy + 3, 1, 1)
            f(clair, 6, hy + 5, 4, 2); f(nez, 7, hy + 4, 2, 1); f(som, 7, hy + 6, 2, 1)
        elif n == "Renard":
            f(clair, 4, hy + 5, 3, 2); f(clair, 9, hy + 5, 3, 2); f(clair, 6, hy + 4, 4, 3); f(nez, 7, hy + 4, 2, 1)
            f(oeil, 5, hy + 3, 1, 2); f(oeil, 10, hy + 3, 1, 2); f(som, 7, hy + 6, 2, 1)
        else:
            f(som, 3, hy + 4, 1, 3); f(som, 12, hy + 4, 1, 3)
            f(clair, 6, hy + 4, 4, 3); f(nez, 7, hy + 4, 2, 1); f(som, 5, hy + 2, 2, 1); f(som, 9, hy + 2, 2, 1)
            f(oeil, 5, hy + 3, 2, 1); f(oeil, 9, hy + 3, 2, 1); f(som, 7, hy + 6, 2, 1)
    else:   # profil gauche
        if n == "Capybara":
            f(clair, 2, hy + 3, 3, 4); f(nez, 2, hy + 3, 1, 2); f(oeil, 5, hy + 2, 1, 2)
        elif n == "Panda":
            f(clair, 3, hy + 4, 2, 2); f(nez, 3, hy + 4, 1, 1); f(som, 5, hy + 2, 2, 3); f(clair, 5, hy + 3, 1, 1)
        elif n == "Renard":
            f(clair, 2, hy + 4, 3, 2); f(nez, 2, hy + 4, 1, 1); f(oeil, 5, hy + 3, 1, 2)
        else:
            f(clair, 1, hy + 4, 4, 2); f(nez, 1, hy + 4, 1, 1); f(oeil, 5, hy + 3, 1, 1); f(som, 5, hy + 2, 2, 1)


# --------------------------------------------------------------------------------------
# Sprites chibi (16x24) - classes jouables, PNJ
# --------------------------------------------------------------------------------------
PEAU = hexc("#e8c09a")

SPECS = {
    "garde_urbain": dict(manteau=hexc("#2e3e58"), manteau2=hexc("#c8a050"), pantalon=hexc("#1c2230"), cheveux=hexc("#3a2a20"),
                         chapeau="casque", chapeau_c=hexc("#8a909a"), masque=hexc("#7a808a"), yeux=hexc("#ffb030"), arme="epee", robe=False),
    "officier": dict(manteau=hexc("#7a1c24"), manteau2=hexc("#e0b848"), pantalon=hexc("#1c1820"), cheveux=hexc("#b8a070"),
                     chapeau="bicorne", chapeau_c=hexc("#20202e"), masque=None, yeux=hexc("#202030"), arme="epee", robe=False),
    "sorciere": dict(manteau=hexc("#5a2a78"), manteau2=hexc("#a060e0"), pantalon=hexc("#2a1438"), cheveux=hexc("#d8d0e8"),
                     chapeau="pointu", chapeau_c=hexc("#34184c"), masque=None, yeux=hexc("#b080ff"), arme="baton", robe=True),
    "moine": dict(manteau=hexc("#24242c"), manteau2=hexc("#e8e0c8"), pantalon=hexc("#18181e"), cheveux=hexc("#403830"),
                  chapeau="capuche", chapeau_c=hexc("#24242c"), masque=hexc("#e8e0c8"), yeux=hexc("#c0a040"), arme="epee", robe=True),
    "harponneur": dict(manteau=hexc("#4a3a2c"), manteau2=hexc("#78a8b8"), pantalon=hexc("#2a2420"), cheveux=hexc("#2a2420"),
                       chapeau="capuche", chapeau_c=hexc("#5a4a38"), masque=hexc("#c8c0a8"), yeux=hexc("#68d0e0"), arme="harpon", robe=False),
    "pnj_marchand": dict(manteau=hexc("#6a8a4a"), manteau2=hexc("#e0c060"), pantalon=hexc("#3a3020"), cheveux=hexc("#7a5030"),
                         chapeau="bicorne", chapeau_c=hexc("#8a5a30"), masque=None, yeux=hexc("#202030"), arme=None, robe=False),
    "pnj_civil": dict(manteau=hexc("#8a7a6a"), manteau2=hexc("#c0b090"), pantalon=hexc("#4a3a30"), cheveux=hexc("#5a4030"),
                      chapeau=None, chapeau_c=None, masque=None, yeux=hexc("#202030"), arme=None, robe=False),
    "pnj_civile": dict(manteau=hexc("#a05a68"), manteau2=hexc("#e8c8a0"), pantalon=hexc("#5a3040"), cheveux=hexc("#a0602c"),
                       chapeau=None, chapeau_c=None, masque=None, yeux=hexc("#202030"), arme=None, robe=True),
    "pnj_sage": dict(manteau=hexc("#3a5a8a"), manteau2=hexc("#e8e8f0"), pantalon=hexc("#24344a"), cheveux=hexc("#d8d8e0"),
                     chapeau="capuche", chapeau_c=hexc("#3a5a8a"), masque=None, yeux=hexc("#80d0ff"), arme="baton", robe=True),
}


def _chibi_brut(spec, direction, frame, arme=True):
    s = surf(16, 24)
    f = lambda c, x, y, w=1, h=1: s.fill(c, (x, y, w, h))
    bob = 1 if frame in (1, 3) else 0
    top = bob  # le haut du corps descend d'1px sur les pas
    cote = direction in ("gauche", "droite")
    dos = direction == "haut"
    E = spec.get("esp")
    peau = E["fur"] if E else PEAU
    main_c = E["sombre"] if E and E["nom"] == "Panda" else peau
    man, man2, pant = spec["manteau"], spec["manteau2"], spec["pantalon"]
    if E:
        _queue(f, E, bob)      # la queue passe derrière le corps
    # jambes
    if not spec["robe"]:
        ya = 21 if frame == 1 else 20
        yb = 21 if frame == 3 else 20
        f(pant, 5, ya, 3, 3 - (ya - 20)); f(pant, 8, yb, 3, 3 - (yb - 20))
        f(sombre(pant, 0.5), 5, 23, 3, 1); f(sombre(pant, 0.5), 8, 23, 3, 1)
    else:
        f(sombre(man, 0.3), 4, 21, 8, 2 - bob)
        f(sombre(man, 0.5), 3 if frame != 3 else 4, 23, 4, 1); f(sombre(man, 0.5), 9, 23, 4 if frame != 1 else 3, 1)
    # corps
    f(man, 4, 14 + top, 8, 6 + (1 if spec["robe"] else 0))
    f(sombre(man, 0.25), 4, 18 + top, 8, 1)  # ceinture
    f(man2, 7, 14 + top, 2, 5) if not cote else f(man2, 7, 14 + top, 1, 5)
    f(man2, 4, 14 + top, 8, 1)  # col
    # bras
    f(sombre(man, 0.15), 3, 15 + top, 1, 4); f(sombre(man, 0.15), 12, 15 + top, 1, 4)
    f(main_c, 3, 19 + top, 1, 1); f(main_c, 12, 19 + top, 1, 1)
    # tête
    hy = 7 + top
    f(peau, 4, hy, 8, 7); f(peau, 5, hy - 1, 6, 1)
    ch = spec["cheveux"]
    if dos:
        f(ch, 4, hy - 1, 8, 8); f(sombre(ch, 0.25), 5, hy + 3, 6, 1)
    else:
        f(ch, 4, hy - 1, 8, 3); f(ch, 4, hy, 1, 4); f(ch, 11, hy, 1, 4)
        f(clair(ch, 0.4), 6, hy - 1, 3, 1); f(sombre(ch, 0.3), 4, hy + 2, 8, 1)      # reflet et frange
        if cote:
            f(ch, 7, hy, 5, 5)
    # visage
    if not dos and not E:
        if cote:
            f(spec["yeux"], 5, hy + 3, 1, 2); f(sombre(peau, 0.2), 4, hy + 5, 1, 1)
        else:
            f(spec["yeux"], 5, hy + 3, 2, 2); f(spec["yeux"], 9, hy + 3, 2, 2)
            f((255, 255, 255), 5, hy + 3, 1, 1); f((255, 255, 255), 9, hy + 3, 1, 1)
            f(sombre(spec["yeux"], 0.55), 5, hy + 4, 2, 1); f(sombre(spec["yeux"], 0.55), 9, hy + 4, 2, 1)
            if spec["masque"] is None:
                f((236, 150, 140), 4, hy + 5, 1, 1); f((236, 150, 140), 11, hy + 5, 1, 1)   # joues
        if spec["masque"] is not None:
            f(spec["masque"], 4 if not cote else 4, hy + 5, 8 if not cote else 4, 2)
            if spec["chapeau"] == "casque":
                f(spec["masque"], 4, hy + 2, 8, 5); f(spec["yeux"], 5, hy + 3, 2, 1); f(spec["yeux"], 9, hy + 3, 2, 1)
    # chapeaux
    h, hc = spec["chapeau"], spec["chapeau_c"]
    if h == "casque":
        f(hc, 3, hy - 3, 10, 4); f(clair(hc, 0.3), 4, hy - 3, 8, 1); f(sombre(hc, 0.4), 3, hy, 10, 1)
    elif h == "bicorne":
        f(hc, 2, hy - 2, 12, 3); f(hc, 4, hy - 4, 8, 2); f(man2 if spec["manteau2"] else hc, 2, hy, 12, 1)
        f(man2, 7, hy - 3, 2, 1)
    elif h == "pointu":
        f(hc, 2, hy - 1, 12, 2); f(hc, 4, hy - 3, 8, 2); f(hc, 5, hy - 5, 6, 2); f(hc, 6, hy - 7, 4, 2); f(hc, 7, hy - 8, 3, 1)
        f(man2, 4, hy - 1, 8, 1)
    elif h == "capuche":
        if E and not dos:        # capuche ajustée : le visage de l'animal reste dégagé
            f(hc, 3, hy - 2, 10, 1); f(hc, 3, hy - 1, 1, 7); f(hc, 12, hy - 1, 1, 7)
        else:
            f(hc, 3, hy - 2, 10, 4); f(hc, 3, hy + 2, 2, 5); f(hc, 11, hy + 2, 2, 5); f(sombre(hc, 0.4), 5, hy + 1, 6, 1)
        if not dos and not E:
            f(sombre(PEAU, 0.55), 5, hy + 2, 6, 4)
            if spec["masque"] is not None:
                f(spec["masque"], 5, hy + 4, 6, 3)
            f(spec["yeux"], 5 if not cote else 5, hy + 3, 2, 1)
            if not cote:
                f(spec["yeux"], 9, hy + 3, 2, 1)
        else:
            f(hc, 3, hy - 2, 10, 9)
    if E:
        if not dos:
            _visage_animal(f, E, "gauche" if cote else "bas", hy)
        _oreilles(f, E, hy)
    # arme tenue (utilisée en combat)
    if arme and spec["arme"] and not dos:
        a = spec["arme"]
        if a == "epee":
            f(hexc("#c8d0d8"), 13, 10 + top, 1, 9); f(hexc("#8a96a2"), 14, 11 + top, 1, 7) if False else None
            f(hexc("#e8c860"), 12, 18 + top, 3, 1)
        elif a == "baton":
            f(hexc("#6a4a30"), 13, 8 + top, 1, 14); f(spec["manteau2"], 12, 5 + top, 3, 3); f((255, 255, 255), 13, 6 + top, 1, 1)
        elif a == "harpon":
            f(hexc("#5a4a38"), 13, 6 + top, 1, 16); f(hexc("#b8c0c8"), 12, 3 + top, 3, 3); f(hexc("#b8c0c8"), 13, 1 + top, 1, 2)
    return s


_cache_chibi = {}


def chibi(spec_nom, direction="bas", frame=0, echelle=1, arme=False, spec=None, contour=True, espece=None):
    """Sprite chibi. `espece` (capybara / panda / renard / loup) donne une tête animale portant le costume de la classe."""
    cle = (spec_nom if spec is None else id(spec), direction, frame, echelle, arme, contour, espece)
    if cle in _cache_chibi:
        return _cache_chibi[cle]
    sp = spec or SPECS[spec_nom]
    if espece:
        e = ESPECES[espece]
        sp = {**sp, "esp": e, "cheveux": e["fur"], "masque": None}
    d = "gauche" if direction == "droite" else direction
    base = ombrer(_chibi_brut(sp, d, frame, arme))
    if direction == "droite":
        base = pygame.transform.flip(base, True, False)
    if contour:
        out = surf(18, 26)
        m = pygame.mask.from_surface(base).to_surface(setcolor=CONTOUR, unsetcolor=(0, 0, 0, 0))
        for dx, dy in ((0, 1), (2, 1), (1, 0), (1, 2)):
            out.blit(m, (dx, dy))
        out.blit(base, (1, 1))
        base = out
    if echelle > 1:
        base = pygame.transform.scale(base, (base.get_width() * echelle, base.get_height() * echelle))
    _cache_chibi[cle] = base
    return base


# --------------------------------------------------------------------------------------
# Monstres (weepers / chiens de brume) et boss
# --------------------------------------------------------------------------------------
def _monstre_brut(couleur, yeux, frame=0, variante=0):
    s = surf(24, 24)
    f = lambda c, x, y, w=1, h=1: s.fill(c, (x, y, w, h))
    c, c2 = couleur, sombre(couleur, 0.35)
    b = frame % 2
    pygame.draw.ellipse(s, c2, (3, 8, 18, 14))
    pygame.draw.ellipse(s, c, (4, 8 + b, 16, 12))
    # dos voûté & épines
    for i in range(5):
        f(c2, 5 + i * 3, 6 + (i % 2) + b, 2, 3)
    # tête
    pygame.draw.ellipse(s, c, (1, 9 + b, 10, 9))
    f(yeux, 3, 12 + b, 2, 2); f(yeux, 7, 12 + b, 2, 2); f((255, 255, 255), 3, 12 + b, 1, 1); f((255, 255, 255), 7, 12 + b, 1, 1)
    f((30, 10, 14), 3, 16 + b, 6, 2)
    for x in (3, 5, 7):
        f((240, 240, 230), x, 16 + b, 1, 1)
    # griffes
    f(c2, 14, 20, 3, 3 - b); f(c2, 6, 20, 3, 3 - (1 - b)); f((230, 230, 220), 14, 23, 1, 1); f((230, 230, 220), 16, 23, 1, 1)
    if variante == 1:   # hurleur : bouche ouverte
        f((10, 0, 8), 2, 15 + b, 8, 4)
    elif variante == 2:  # écorcheur : lames sur le bras
        f((220, 220, 230), 18, 12 + b, 1, 8); f((220, 220, 230), 19, 14 + b, 1, 6)
    elif variante == 3:  # brute : épaules massives
        pygame.draw.ellipse(s, c, (13, 6 + b, 10, 8))
    return s


def monstre(variante=0, void=False, echelle=2, frame=0):
    cle = ("monstre", variante, void, echelle, frame)
    if cle in _cache_chibi:
        return _cache_chibi[cle]
    c = [hexc("#5a7064"), hexc("#6a5a74"), hexc("#7a4a44"), hexc("#4a5a3a")][variante % 4]
    yeux = hexc("#ff3030")
    if void:
        c = mix(c, hexc("#4a3aa0"), 0.6); yeux = hexc("#a0e0ff")
    base = ombrer(_monstre_brut(c, yeux, frame, variante % 4))
    out = surf(26, 26)
    m = pygame.mask.from_surface(base).to_surface(setcolor=CONTOUR, unsetcolor=(0, 0, 0, 0))
    for dx, dy in ((0, 1), (2, 1), (1, 0), (1, 2)):
        out.blit(m, (dx, dy))
    out.blit(base, (1, 1))
    out = pygame.transform.scale(out, (26 * echelle, 26 * echelle))
    _cache_chibi[cle] = out
    return out


BOSS_SPECS = {
    "reine_ronce": dict(manteau=hexc("#2a5a30"), manteau2=hexc("#e8d040"), pantalon=hexc("#1a3a20"), cheveux=hexc("#a0d070"),
                        chapeau="pointu", chapeau_c=hexc("#1c3a22"), masque=None, yeux=hexc("#f0e050"), arme="baton", robe=True),
    "prevot": dict(manteau=hexc("#1a2438"), manteau2=hexc("#d8b040"), pantalon=hexc("#10141e"), cheveux=hexc("#aaaaaa"),
                   chapeau="casque", chapeau_c=hexc("#9aa0aa"), masque=hexc("#8a909a"), yeux=hexc("#ff5030"), arme="epee", robe=False),
    "abbesse": dict(manteau=hexc("#e8e0d0"), manteau2=hexc("#d8a830"), pantalon=hexc("#c8c0b0"), cheveux=hexc("#e8e8e8"),
                    chapeau="capuche", chapeau_c=hexc("#d8d0c0"), masque=hexc("#d8a830"), yeux=hexc("#ff8030"), arme="baton", robe=True),
    "kael": dict(manteau=hexc("#1c3a6a"), manteau2=hexc("#60e0ff"), pantalon=hexc("#101c38"), cheveux=hexc("#101830"),
                 chapeau="capuche", chapeau_c=hexc("#243a70"), masque=hexc("#a0c8e8"), yeux=hexc("#80ffff"), arme="harpon", robe=False),
    "ossian": dict(manteau=hexc("#4a3a8a"), manteau2=hexc("#c0a0ff"), pantalon=hexc("#1a1440"), cheveux=hexc("#c8c0e8"),
                   chapeau="bicorne", chapeau_c=hexc("#241a50"), masque=None, yeux=hexc("#e0a0ff"), arme="epee", robe=False),
    "vaerith": dict(manteau=hexc("#0e0a18"), manteau2=hexc("#a040ff"), pantalon=hexc("#08060e"), cheveux=hexc("#e8e0ff"),
                    chapeau="capuche", chapeau_c=hexc("#14101e"), masque=hexc("#2a2040"), yeux=hexc("#ff40ff"), arme="baton", robe=True),
}


def boss(nom, echelle=4, frame=0):
    cle = ("boss", nom, echelle, frame)
    if cle in _cache_chibi:
        return _cache_chibi[cle]
    sp = BOSS_SPECS[nom]
    base = chibi(None, "bas", frame, 1, True, spec=sp)
    # couronne / halo
    ex = surf(18, 26); ex.blit(base, (0, 0))
    pygame.draw.polygon(ex, sp["manteau2"], [(4, 4), (6, 1), (9, 4), (12, 1), (14, 4)]) if nom in ("reine_ronce", "vaerith", "abbesse") else None
    out = pygame.transform.scale(ex, (18 * echelle, 26 * echelle))
    _cache_chibi[cle] = out
    return out


# --------------------------------------------------------------------------------------
# Icônes d'objets (12x12)
# --------------------------------------------------------------------------------------
RARETE_COULEURS = [hexc("#c8c8c8"), hexc("#68d060"), hexc("#5090ff"), hexc("#c060ff"), hexc("#ff9030"), hexc("#ffe060")]
RARETE_NOMS = ["Commun", "Peu commun", "Rare", "Très rare", "Épique", "Légendaire"]


def icone(forme, couleur=(200, 200, 200), rarete=0):
    cle = ("icone", forme, couleur, rarete)
    if cle in _cache_chibi:
        return _cache_chibi[cle]
    s = surf(12, 12)
    f = lambda c, x, y, w=1, h=1: s.fill(c, (x, y, w, h))
    if forme == "potion":
        f((230, 230, 240), 5, 1, 2, 2); f((150, 110, 70), 5, 0, 2, 1); pygame.draw.ellipse(s, (230, 230, 240), (2, 3, 8, 8)); pygame.draw.ellipse(s, couleur, (3, 5, 6, 5))
        f((255, 255, 255), 4, 4, 1, 1)
    elif forme == "epee":
        for i in range(8):
            f(couleur, 8 - i, 1 + i, 1, 1); f(clair(couleur, 0.4), 9 - i, 1 + i, 1, 1)
        f((200, 160, 60), 1, 7, 4, 1); f((200, 160, 60), 3, 5, 1, 4); f((120, 80, 40), 1, 10, 2, 1)
    elif forme == "talisman":
        pygame.draw.polygon(s, couleur, [(6, 0), (11, 6), (6, 11), (1, 6)]); pygame.draw.polygon(s, sombre(couleur, 0.5), [(6, 3), (8, 6), (6, 9), (4, 6)])
        f((255, 255, 255), 6, 5, 1, 1)
    elif forme == "rune":
        pygame.draw.circle(s, sombre(couleur, 0.6), (6, 6), 5); pygame.draw.circle(s, couleur, (6, 6), 5, 1)
        f(couleur, 6, 2, 1, 8); f(couleur, 4, 4, 5, 1); f(couleur, 3, 8, 3, 1)
    elif forme == "plume":
        pygame.draw.line(s, (120, 50, 20), (1, 11), (5, 7), 1)
        pygame.draw.polygon(s, couleur, [(4, 8), (8, 1), (11, 2), (10, 6), (6, 9)])
        pygame.draw.polygon(s, (255, 220, 90), [(8, 1), (11, 2), (10, 4), (8, 4)])
        pygame.draw.line(s, (255, 250, 200), (5, 8), (10, 3))
    elif forme == "grenade":
        pygame.draw.circle(s, (70, 76, 84), (6, 7), 4); f((200, 160, 60), 5, 2, 3, 2); f((255, 160, 60), 8, 1, 1, 1)
    elif forme == "or":
        pygame.draw.circle(s, (230, 190, 60), (6, 6), 5); pygame.draw.circle(s, (160, 120, 30), (6, 6), 5, 1); f((255, 240, 150), 4, 4, 2, 1)
    elif forme == "livre":
        f((120, 40, 40), 2, 2, 8, 9); f((230, 210, 160), 3, 3, 6, 7); f((120, 40, 40), 5, 3, 1, 7)
    else:
        f(couleur, 2, 2, 8, 8)
    out = surf(12, 12)
    m = pygame.mask.from_surface(s).to_surface(setcolor=CONTOUR, unsetcolor=(0, 0, 0, 0))
    big = surf(14, 14)
    for dx, dy in ((0, 1), (2, 1), (1, 0), (1, 2)):
        big.blit(m, (dx, dy))
    big.blit(s, (1, 1))
    _cache_chibi[cle] = big
    return big


# --------------------------------------------------------------------------------------
# Décors de combat 480x270
# --------------------------------------------------------------------------------------
def _degrade(s, haut, bas, y0=0, y1=None):
    y1 = y1 if y1 is not None else s.get_height()
    for y in range(y0, y1):
        t = (y - y0) / max(1, y1 - y0 - 1)
        pygame.draw.line(s, mix(haut, bas, t), (0, y), (s.get_width(), y))


def fond_combat(biome, monde="realme", seed=1):
    cle = ("fond", biome, monde)
    if cle in _cache_chibi:
        return _cache_chibi[cle]
    rng = random.Random(seed)
    W, H = 480, 270
    s = pygame.Surface((W, H))
    horizon = 150
    if monde == "void":
        _degrade(s, hexc("#06041a"), hexc("#3a1e78"), 0, horizon + 40)
        for _ in range(110):
            s.set_at((rng.randrange(W), rng.randrange(horizon)), rng.choice([hexc("#a0b0ff"), hexc("#ffffff"), hexc("#c080ff")]))
        # fragments flottants (gravité inversée : îlots suspendus la tête en bas)
        for _ in range(9):
            x, y = rng.randrange(W), rng.randrange(20, 130); w = rng.randint(30, 90)
            pts = [(x, y), (x + w, y), (x + w * 0.7, y + w * 0.35), (x + w * 0.5, y + w * 0.7), (x + w * 0.3, y + w * 0.3)]
            pygame.draw.polygon(s, hexc("#201650"), pts); pygame.draw.polygon(s, hexc("#4a3aa0"), pts, 1)
            pygame.draw.line(s, hexc("#8060ff"), (x, y), (x + w, y))
        pygame.draw.circle(s, hexc("#0a0620"), (360, 70), 34); pygame.draw.circle(s, hexc("#a060ff"), (360, 70), 36, 2)  # l'Œil du Void
        pygame.draw.circle(s, hexc("#d0a0ff"), (360, 70), 8)
        sol = (hexc("#1c1a48"), hexc("#0a0820"))
    elif biome == "foret":
        _degrade(s, hexc("#9aa888"), hexc("#d8d890"), 0, horizon)
        for i in range(9):
            x = i * 60 + rng.randint(-10, 10)
            pygame.draw.rect(s, hexc("#8a9a80"), (x, 0, 18, horizon))
        for i in range(11):
            x = i * 48 + rng.randint(-15, 15)
            pygame.draw.rect(s, hexc("#2e4a2a"), (x, 0, 22, horizon + 6)); pygame.draw.rect(s, hexc("#1c3320"), (x + 14, 0, 8, horizon + 6))
        for _ in range(30):
            pygame.draw.circle(s, hexc("#3f7a34"), (rng.randrange(W), rng.randint(0, 50)), rng.randint(14, 28))
        sol = (hexc("#5a9040"), hexc("#25502a"))
    elif biome == "donjon":
        _degrade(s, hexc("#0a0c0a"), hexc("#2a2e26"), 0, horizon)
        for i in range(6):
            x = 20 + i * 90
            pygame.draw.rect(s, hexc("#3a3c34"), (x, 40, 40, horizon - 40)); pygame.draw.circle(s, hexc("#3a3c34"), (x + 20, 40), 20)
            pygame.draw.rect(s, hexc("#080a08"), (x + 8, 52, 24, horizon - 52)); pygame.draw.circle(s, hexc("#080a08"), (x + 20, 52), 12)
            if i % 2 == 0:
                pygame.draw.circle(s, hexc("#f08a30"), (x + 20, 90), 5); pygame.draw.circle(s, hexc("#ffd070"), (x + 20, 89), 2)
        sol = (hexc("#2c3a30"), hexc("#141a16"))
    elif biome == "ouvert":
        _degrade(s, hexc("#b8b090"), hexc("#f0e0a8"), 0, horizon)
        pygame.draw.rect(s, hexc("#3f6e8c"), (0, horizon - 36, W, 36))
        for y in range(horizon - 34, horizon, 5):
            pygame.draw.line(s, hexc("#7eb0c8"), (rng.randrange(0, 200), y), (rng.randrange(200, 480), y))
        for x in range(0, W, 120):
            pygame.draw.polygon(s, hexc("#6a6a62"), [(x, horizon - 36), (x + 40, 60), (x + 90, horizon - 36)])
        sol = (hexc("#9aa060"), hexc("#4a6a30"))
    else:  # ville : silhouette de Dunwall
        _degrade(s, hexc("#7a3a3a"), hexc("#f0a850"), 0, horizon)
        pygame.draw.circle(s, hexc("#ffe0a0"), (380, 96), 26)
        for i in range(14):
            x = i * 38 + rng.randint(-6, 6); h = rng.randint(50, 110)
            pygame.draw.rect(s, hexc("#4a2a2e"), (x, horizon - h, 34, h))
            pygame.draw.polygon(s, hexc("#2e1a22"), [(x - 3, horizon - h), (x + 17, horizon - h - 18), (x + 37, horizon - h)])
            for wy in range(horizon - h + 10, horizon - 10, 14):
                if rng.random() < 0.5:
                    pygame.draw.rect(s, hexc("#ffc860"), (x + 6 + rng.choice([0, 14]), wy, 6, 8))
            if rng.random() < 0.4:
                pygame.draw.rect(s, hexc("#2e1a22"), (x + 24, horizon - h - 30, 5, 30))
        sol = (hexc("#b89050"), hexc("#6a4a30"))
    # sol
    _degrade(s, sol[0], sol[1], horizon, H)
    for i in range(14):
        y = horizon + int((i / 14) ** 1.6 * (H - horizon))
        pygame.draw.line(s, mix(sol[0], sol[1], 0.6), (0, y), (W, y))
    for _ in range(80):
        s.set_at((rng.randrange(W), rng.randrange(horizon, H)), mix(sol[0], (255, 255, 255), 0.2))
    # rayons de lumière obliques
    rayons = surf(W, H)
    col = (170, 140, 255, 20) if monde == "void" else ((255, 230, 160, 24) if biome in ("ville", "ouvert", "foret") else (255, 170, 90, 18))
    for x0 in (60, 190, 330, 430):
        pygame.draw.polygon(rayons, col, [(x0, 0), (x0 + 26, 0), (x0 + 120, horizon + 60), (x0 + 70, horizon + 60)])
    s.blit(rayons, (0, 0))
    # éléments de premier plan (silhouettes sombres qui encadrent l'action)
    noir = (10, 8, 16)
    if monde == "void":
        for sx, sy, k in ((0, 262, 1), (480, 262, -1)):
            pygame.draw.polygon(s, noir, [(sx, sy), (sx + k * 90, sy), (sx + k * 60, sy - 34), (sx + k * 30, sy - 22), (sx, sy - 52)])
            pygame.draw.line(s, (120, 80, 220), (sx, sy - 52), (sx + k * 30, sy - 22))
    elif biome == "foret":
        for sx, k in ((0, 1), (480, -1)):
            pygame.draw.rect(s, noir, (sx - (0 if k > 0 else 22), 0, 22, H))
            for i in range(7):
                pygame.draw.polygon(s, (16, 34, 20), [(sx, 262 - i * 8), (sx + k * (50 + i * 3), 270 - i * 5), (sx + k * 12, 270 - i * 8 - 12)])
    elif biome == "donjon":
        for sx, k in ((14, 1), (466, -1)):
            pygame.draw.rect(s, noir, (sx - 9, 0, 18, H)); pygame.draw.rect(s, (60, 60, 54), (sx - 9, 0, 3, H))
            for y in range(20, 240, 24):
                pygame.draw.circle(s, (96, 96, 86), (sx + k * 14, y), 4, 1)
    else:
        for sx, k in ((26, 1), (454, -1)):
            pygame.draw.rect(s, noir, (sx - 2, 70, 4, 200)); pygame.draw.rect(s, noir, (sx - 8, 62, 16, 10))
            pygame.draw.rect(s, (255, 200, 110), (sx - 5, 64, 10, 6))
            pygame.draw.circle(s, (255, 190, 100, 0), (sx, 66), 3)
    # vignette
    v = surf(W, H)
    for r in range(0, 90, 3):
        pygame.draw.rect(v, (0, 0, 0, 3 + r // 6 if False else int(60 * (1 - r / 90))), (r, r, W - 2 * r, H - 2 * r), 3)
    s.blit(v, (0, 0))
    _cache_chibi[cle] = s
    return s


def lumiere(rayon, couleur=(255, 255, 255)):
    """Disque de lumière doux (pour l'ambiance : multiplication sur une couche sombre)."""
    cle = ("lum", rayon, couleur)
    if cle in _cache_chibi:
        return _cache_chibi[cle]
    s = pygame.Surface((rayon * 2, rayon * 2))
    s.fill((0, 0, 0))
    for r in range(rayon, 0, -2):
        t = 1 - r / rayon
        c = tuple(int(v * min(1, t * 1.5) ** 1.2) for v in couleur)
        pygame.draw.circle(s, c, (rayon, rayon), r)
    _cache_chibi[cle] = s
    return s


def coffre(ouvert=False, rarete=3):
    cle = ("coffre", ouvert, rarete)
    if cle in _cache_chibi:
        return _cache_chibi[cle]
    s = surf(16, 16)
    bois, fer = hexc("#7a4a28"), RARETE_COULEURS[min(5, rarete)]
    pygame.draw.rect(s, sombre(bois, 0.5), (1, 6, 14, 9))
    pygame.draw.rect(s, bois, (2, 7, 12, 7))
    if ouvert:
        pygame.draw.rect(s, sombre(bois, 0.4), (2, 2, 12, 5)); pygame.draw.rect(s, (30, 20, 20), (3, 3, 10, 3))
        pygame.draw.rect(s, (250, 220, 110), (4, 6, 8, 2))
    else:
        pygame.draw.rect(s, sombre(bois, 0.2), (1, 3, 14, 5)); pygame.draw.rect(s, bois, (2, 4, 12, 3))
        pygame.draw.rect(s, fer, (7, 6, 2, 3))
    pygame.draw.rect(s, fer, (1, 6, 14, 1)); pygame.draw.rect(s, fer, (3, 7, 1, 7)); pygame.draw.rect(s, fer, (12, 7, 1, 7))
    _cache_chibi[cle] = s
    return s


def teinter(image, couleur):
    """Multiplie l'image par une couleur (monstres spectraux du Void)."""
    cle = ("teinte", id(image), couleur)
    if cle not in _cache_chibi:
        t = image.copy()
        t.fill(couleur + (255,), special_flags=pygame.BLEND_RGBA_MULT)
        _cache_chibi[cle] = t
    return _cache_chibi[cle]


def vignette(force=150):
    """Assombrissement doux des bords (cache)."""
    cle = ("vignette", force)
    if cle in _cache_chibi:
        return _cache_chibi[cle]
    pet = surf(48, 27)
    for y in range(27):
        for x in range(48):
            d = math.hypot((x - 23.5) / 24, (y - 13) / 13.5)
            a = max(0.0, (d - 0.62) / 0.7)
            pet.set_at((x, y), (4, 2, 12, int(min(1.0, a * a) * force)))
    v = pygame.transform.smoothscale(pet, (480, 270))
    _cache_chibi[cle] = v
    return v


def degrade_vertical(w, h, haut, bas):
    s = pygame.Surface((w, h))
    for y in range(h):
        pygame.draw.line(s, mix(haut, bas, y / max(1, h - 1)), (0, y), (w, y))
    return s
