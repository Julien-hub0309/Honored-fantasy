"""Moteur de cartes partagé : constantes de tuiles, générateurs procéduraux, tileset et rendu par lots (batch).

Les dossiers map/<monde>/<zone>/ ne contiennent que la configuration spécifique à la zone et délèguent ici.
"""
import math
import random
from collections import deque

import pygame

from assets import pixelart as px

T = 16
# ---- identifiants de tuiles -------------------------------------------------------------
SOL, MUR, HERBE, EAU, SORTIE_PREV, SORTIE_NEXT, SUR, TOIT, FACADE, PORTE, TORCHE, ARBRE, FONTAINE, AUTEL = range(14)
DECOR1, DECOR2, DECOR3 = 20, 21, 22
SOLIDES = {MUR, EAU, TOIT, FACADE, PORTE, TORCHE, ARBRE, FONTAINE, AUTEL, DECOR1, DECOR2, DECOR3}
ANIMEES = {EAU, HERBE, TORCHE, SORTIE_PREV, SORTIE_NEXT, AUTEL, FONTAINE}


class Zone:
    def __init__(self, nom, monde, biome, pal, niveau, w, h):
        self.nom, self.monde, self.biome, self.pal, self.niveau, self.w, self.h = nom, monde, biome, pal, niveau, w, h
        self.tuiles = [[MUR] * w for _ in range(h)]
        self.entree_prev = (1, 1)
        self.entree_next = (w - 2, 1)
        self.pnjs, self.coffres, self.boss, self.autels, self.lumieres = [], [], [], [], []
        self.slots = {}          # emplacements nommés pour placer PNJ / objets
        self.ambiance = (255, 255, 255)
        self.musique = "foret"
        self.prosperite = 1
        self.sur = False

    def tuile(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.tuiles[y][x]
        return MUR

    def solide(self, x, y):
        return self.tuile(x, y) in SOLIDES

    def libre(self, x, y):
        return not self.solide(x, y) and (x, y) not in self.occupes

    @property
    def occupes(self):
        return {(p["x"], p["y"]) for p in self.pnjs} | {(c["x"], c["y"]) for c in self.coffres} | \
               {(b["x"], b["y"]) for b in self.boss} | set(self.autels)


# --------------------------------------------------------------------------------------
# Utilitaires de génération
# --------------------------------------------------------------------------------------
def _remplir(z, x0, y0, x1, y1, t):
    for y in range(max(0, y0), min(z.h, y1 + 1)):
        for x in range(max(0, x0), min(z.w, x1 + 1)):
            z.tuiles[y][x] = t


def accessibles(z, depart):
    vus = {depart}
    q = deque([depart])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n not in vus and 0 <= n[0] < z.w and 0 <= n[1] < z.h and z.tuiles[n[1]][n[0]] not in SOLIDES:
                vus.add(n)
                q.append(n)
    return vus


def distances(z, depart):
    d = {depart: 0}
    q = deque([depart])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n not in d and 0 <= n[0] < z.w and 0 <= n[1] < z.h and z.tuiles[n[1]][n[0]] not in SOLIDES:
                d[n] = d[(x, y)] + 1
                q.append(n)
    return d


def cases_libres(z, zone_acces, rng, n, eviter=(), dist_min=3, sur_types=(SOL, HERBE)):
    """Retourne jusqu'à n cases libres atteignables, espacées d'au moins dist_min."""
    if n <= 0:
        return []
    cand = [c for c in zone_acces if z.tuile(*c) in sur_types and c not in z.occupes]
    rng.shuffle(cand)
    choisies = []
    for c in cand:
        if all(abs(c[0] - o[0]) + abs(c[1] - o[1]) >= dist_min for o in list(eviter) + choisies):
            choisies.append(c)
            if len(choisies) >= n:
                break
    return choisies


# --------------------------------------------------------------------------------------
# Village
# --------------------------------------------------------------------------------------
def gen_village(z, rng):
    w, h = z.w, z.h
    _remplir(z, 0, 0, w - 1, h - 1, SOL)
    _remplir(z, 0, 0, w - 1, 0, MUR); _remplir(z, 0, h - 1, w - 1, h - 1, MUR)
    _remplir(z, 0, 0, 0, h - 1, MUR); _remplir(z, w - 1, 0, w - 1, h - 1, MUR)
    ya = h // 2 - 1                                  # avenue principale (3 cases)
    rues_x = [w // 4 - 1, w // 2 - 1, 3 * w // 4 - 1]  # rues verticales (2 cases)
    colonnes = [1] + [x + 2 for x in rues_x]
    fins = [x - 1 for x in rues_x] + [w - 2]
    boutiques = []
    for (bx0, bx1) in zip(colonnes, fins):
        for (by0, by1) in ((1, ya - 1), (ya + 4, h - 2)):      # blocs au nord et au sud de l'avenue
            if by1 - by0 < 3 or bx1 - bx0 < 3:
                continue
            x = bx0
            while x <= bx1 - 2:
                bw = min(rng.randint(4, 7), bx1 - x + 1)
                if bx1 - (x + bw) < 3:
                    bw = bx1 - x + 1
                _remplir(z, x, by0, x + bw - 1, by1 - 2, TOIT)
                _remplir(z, x, by1 - 1, x + bw - 1, by1 - 1, FACADE)
                px_ = x + bw // 2
                z.tuiles[by1 - 1][px_] = PORTE
                if by1 < ya:
                    boutiques.append((px_, by1))              # case devant la porte (côté avenue)
                x += bw + 1 if bw + 1 <= bx1 - x else bw
    # plaza centrale (zone sûre) + fontaine
    cx = rues_x[1] + 1
    _remplir(z, cx - 5, ya - 3, cx + 5, ya + 5, SUR)
    z.tuiles[ya + 1][cx] = FONTAINE
    z.autels.append((cx - 3, ya + 1)); z.tuiles[ya + 1][cx - 3] = AUTEL
    # lampadaires (solides, éclairent) et décors
    for lx in range(4, w - 3, 7):
        for ly in (ya - 1, ya + 3):
            if z.tuiles[ly][lx] in (SOL,):
                z.tuiles[ly][lx] = DECOR1
                z.lumieres.append((lx, ly, 58, (255, 200, 110)))
    for _ in range(int(w * h * 0.012)):
        x, y = rng.randrange(2, w - 2), rng.randrange(2, h - 2)
        if z.tuiles[y][x] == SOL and abs(y - (ya + 1)) > 1 and not (cx - 5 <= x <= cx + 5):
            z.tuiles[y][x] = rng.choice((DECOR2, DECOR3))
    # sorties
    z.tuiles[ya + 1][0] = SORTIE_PREV
    z.tuiles[ya + 1][w - 1] = SORTIE_NEXT
    z.entree_prev = (1, ya + 1)
    z.entree_next = (w - 2, ya + 1)
    acces = accessibles(z, z.entree_prev)
    z.slots["plaza"] = [c for c in acces if c in {(x, y) for x in range(cx - 5, cx + 6) for y in range(ya - 3, ya + 6)} and z.tuile(*c) == SUR]
    z.slots["boutiques"] = [b for b in boutiques if b in acces]
    z.slots["rues"] = [c for c in acces if z.tuile(*c) == SOL]
    z.slots["acces"] = acces
    z.sur = True


# --------------------------------------------------------------------------------------
# Nature (forêt, plaines / falaises, Void ouvert)
# --------------------------------------------------------------------------------------
def gen_nature(z, rng, densite=0.45, herbe=0.5, eau=0.012, decor=0.02):
    w, h = z.w, z.h
    t = [[ARBRE if (rng.random() < densite or x in (0, w - 1) or y in (0, h - 1)) else SOL for x in range(w)] for y in range(h)]
    for _ in range(4):                                # automate cellulaire : grottes végétales
        n = [row[:] for row in t]
        for y in range(1, h - 1):
            for x in range(1, w - 1):
                m = sum(1 for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dx or dy) and t[y + dy][x + dx] == ARBRE)
                n[y][x] = ARBRE if m >= 5 else (SOL if m <= 3 else t[y][x])
        t = n
    z.tuiles = t
    ymid = h // 2
    y = ymid                                           # sentier sinueux gauche -> droite (largeur 3)
    for x in range(1, w - 1):
        y = max(4, min(h - 5, y + rng.choice((-1, 0, 0, 0, 1))))
        for dy in (-1, 0, 1):
            z.tuiles[y + dy][x] = SOL
    # couloir d'entrée / clairière de boss
    ye = z.tuiles and ymid
    _remplir(z, 1, ymid - 1, 4, ymid + 1, SOL)
    _remplir(z, w - 14, ymid - 4, w - 6, ymid + 4, SOL)       # clairière
    _remplir(z, w - 6, ymid, w - 2, ymid, SOL)               # goulet menant à la sortie
    for dy in (-1, 1):
        _remplir(z, w - 6, ymid + dy, w - 2, ymid + dy, ARBRE)
    z.tuiles[ymid][0] = SORTIE_PREV
    z.tuiles[ymid][w - 1] = SORTIE_NEXT
    z.entree_prev, z.entree_next = (1, ymid), (w - 2, ymid)
    z.boss_pos = (w - 4, ymid)
    # on ne garde que la partie connexe
    acces = accessibles(z, z.entree_prev)
    for yy in range(h):
        for xx in range(w):
            if (xx, yy) not in acces and z.tuiles[yy][xx] not in (SORTIE_PREV, SORTIE_NEXT):
                z.tuiles[yy][xx] = ARBRE
    # herbes hautes (zones à forte densité de rencontres), mares, décors
    for _ in range(max(4, int(w * h * 0.004 * herbe * 4))):
        cx, cy, r = rng.randrange(3, w - 10), rng.randrange(3, h - 3), rng.randint(3, 6)
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if 0 < xx < w - 1 and 0 < yy < h - 1 and z.tuiles[yy][xx] == SOL and (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r * rng.uniform(0.5, 1.0):
                    z.tuiles[yy][xx] = HERBE
    for _ in range(max(1, int(w * h * eau / 6))):
        cx, cy, r = rng.randrange(6, w - 16), rng.randrange(4, h - 4), rng.randint(1, 3)
        if abs(cy - ymid) < 4:
            continue
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if z.tuiles[yy][xx] in (SOL, HERBE) and (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    z.tuiles[yy][xx] = EAU
    acces = accessibles(z, z.entree_prev)
    if z.entree_next not in acces:                      # sécurité : rouvre un passage
        for x in range(1, w - 1):
            if z.tuiles[ymid][x] in SOLIDES:
                z.tuiles[ymid][x] = SOL
        acces = accessibles(z, z.entree_prev)
    for c in cases_libres(z, acces, rng, int(w * h * decor), dist_min=2):
        if abs(c[1] - ymid) > 1 and c[0] > 6 and c[0] < w - 15:
            z.tuiles[c[1]][c[0]] = rng.choice((DECOR1, DECOR2, DECOR3))
    z.slots["acces"] = accessibles(z, z.entree_prev)
    z.slots["loin"] = [c for c in z.slots["acces"] if abs(c[1] - ymid) > 3 and 8 < c[0] < w - 16 and z.tuile(*c) in (SOL, HERBE)]


# --------------------------------------------------------------------------------------
# Donjon (BSP)
# --------------------------------------------------------------------------------------
def gen_donjon(z, rng, mid_boss=False):
    w, h = z.w, z.h
    _remplir(z, 0, 0, w - 1, h - 1, MUR)
    feuilles = []

    def decouper(x0, y0, x1, y1, prof):
        lw, lh = x1 - x0 + 1, y1 - y0 + 1
        if prof >= 4 or (lw < 18 and lh < 14):
            feuilles.append((x0, y0, x1, y1)); return None
        vertical = lw > lh * 1.2 if lw != lh else rng.random() < 0.5
        if vertical and lw >= 18:
            c = rng.randint(x0 + 8, x1 - 8)
            a, b = decouper(x0, y0, c - 1, y1, prof + 1), decouper(c, y0, x1, y1, prof + 1)
        elif lh >= 14:
            c = rng.randint(y0 + 6, y1 - 6)
            a, b = decouper(x0, y0, x1, c - 1, prof + 1), decouper(x0, c, x1, y1, prof + 1)
        else:
            feuilles.append((x0, y0, x1, y1)); return None
        return a, b

    def salle_de(feu):
        x0, y0, x1, y1 = feu
        rw, rh = rng.randint(6, max(6, x1 - x0 - 3)), rng.randint(5, max(5, y1 - y0 - 3))
        rx, ry = rng.randint(x0 + 1, max(x0 + 1, x1 - rw - 1)), rng.randint(y0 + 1, max(y0 + 1, y1 - rh - 1))
        return (rx, ry, min(x1 - 1, rx + rw - 1), min(y1 - 1, ry + rh - 1))

    decouper(1, 1, w - 2, h - 2, 0)
    salles = [salle_de(f) for f in feuilles]
    salles.sort(key=lambda s: s[0])
    for s in salles:
        _remplir(z, s[0], s[1], s[2], s[3], SOL)

    def centre(s):
        return ((s[0] + s[2]) // 2, (s[1] + s[3]) // 2)

    def couloir(a, b):
        (x0, y0), (x1, y1) = centre(a), centre(b)
        for x in range(min(x0, x1), max(x0, x1) + 1):
            z.tuiles[y0][x] = SOL
            if y0 + 1 < h - 1:
                z.tuiles[y0 + 1][x] = SOL
        for y in range(min(y0, y1), max(y0, y1) + 1):
            z.tuiles[y][x1] = SOL
            if x1 + 1 < w - 1:
                z.tuiles[y][x1 + 1] = SOL

    for a, b in zip(salles, salles[1:]):
        couloir(a, b)
    if len(salles) > 3:
        couloir(salles[0], salles[2]) if rng.random() < 0.5 else couloir(salles[1], salles[-1])
    # décors dans les salles
    for s in salles[1:-1]:
        if s[2] - s[0] >= 7 and s[3] - s[1] >= 6:
            for px_, py_ in ((s[0] + 1, s[1] + 1), (s[2] - 1, s[1] + 1), (s[0] + 1, s[3] - 1), (s[2] - 1, s[3] - 1)):
                if rng.random() < 0.7:
                    z.tuiles[py_][px_] = DECOR1
        for _ in range(rng.randint(0, 3)):
            x, y = rng.randint(s[0], s[2]), rng.randint(s[1], s[3])
            if z.tuiles[y][x] == SOL:
                z.tuiles[y][x] = rng.choice((DECOR2, DECOR3))
    # entrée / sortie
    s0, s1 = salles[0], salles[-1]
    ey = centre(s0)[1]
    sx = s0[0]
    z.tuiles[ey][sx - 1] = SORTIE_PREV
    z.entree_prev = (sx, ey)
    fy = centre(s1)[1]
    z.tuiles[fy][s1[2] + 1] = SORTIE_NEXT
    z.entree_next = (s1[2], fy)
    z.boss_pos = (s1[2] - 2, fy)
    if z.tuile(*z.boss_pos) in SOLIDES:
        z.tuiles[z.boss_pos[1]][z.boss_pos[0]] = SOL
    if mid_boss:
        mid = salles[len(salles) // 2 + (1 if len(salles) > 4 else 0)]
        z.mid_boss_pos = centre(mid)
        z.tuiles[z.mid_boss_pos[1]][z.mid_boss_pos[0]] = SOL
    # torches murales : murs situés juste au-dessus d'une case de sol
    for y in range(1, h - 1):
        for x in range(2, w - 2):
            if z.tuiles[y][x] == MUR and z.tuiles[y + 1][x] == SOL and z.tuiles[y][x - 1] != SORTIE_PREV and rng.random() < 0.09:
                z.tuiles[y][x] = TORCHE
                z.lumieres.append((x, y + 1, 64, (255, 160, 70)))
    acces = accessibles(z, z.entree_prev)
    z.slots["acces"] = acces
    z.salles = salles
    z.slots["salles"] = [s for s in salles[1:-1]]


# --------------------------------------------------------------------------------------
# Tileset + rendu par lots (batch)
# --------------------------------------------------------------------------------------
def construire_tileset(pal, sol="pave", mur="brique", sur="sur", arbre="arbre", eau="eau", decors=("tonneau", "caisse", "statue"),
                       herbe_sol="terre", fond_decor=None, sortie_pal=None):
    """Retourne {id_tuile: [frame0, frame1]} ; les tuiles animées ont 2 frames."""
    p = pal
    f = px.fabriquer_tuile
    ts = {}
    for i in (0, 1):
        ts.setdefault(SOL, []).append(f(sol, p, seed=1) if i == 0 else ts[SOL][0])
    ts[MUR] = [f("mur", p, mur=mur, seed=2)] * 2
    ts[HERBE] = [f("herbe_haute", p, frame=i, seed=3) for i in (0, 1)]
    ts[EAU] = [f(eau, p, frame=i, seed=4) for i in (0, 1)]
    ts[SORTIE_PREV] = ts[SORTIE_NEXT] = [f("sortie", sortie_pal or p, frame=i, seed=5) for i in (0, 1)]
    ts[SUR] = [f(sur, p, seed=6)] * 2
    ts[TOIT] = [f("toit", p, seed=7)] * 2
    ts[FACADE] = [f("facade", p, mur=mur, seed=8)] * 2
    ts[PORTE] = [f("porte", p, mur=mur, seed=9)] * 2
    ts[TORCHE] = [f("torche", p, mur=mur, frame=i, seed=10) for i in (0, 1)]
    ts[ARBRE] = [f(arbre, p, sol=sol, seed=11)] * 2
    ts[FONTAINE] = [f("fontaine", p, frame=i, seed=12) for i in (0, 1)]
    ts[AUTEL] = [f("autel", p, frame=i, seed=13) for i in (0, 1)]
    for t, k in zip((DECOR1, DECOR2, DECOR3), decors):
        ts[t] = [f(k, p, sol=sol, seed=14 + t)] * 2
    # variantes des tuiles très répétées (sol, mur, zone sûre) : brisent l'effet de quadrillage
    ts["var"] = {SOL: [f(sol, p, seed=100 + i) for i in range(6)], MUR: [f("mur", p, mur=mur, seed=200 + i) for i in range(4)],
                 SUR: [f(sur, p, seed=300 + i) for i in range(4)], TOIT: [f("toit", p, seed=400 + i) for i in range(6)]}
    return ts


class Batch:
    """Pré-rend la couche statique de la carte une seule fois ; seules les tuiles animées sont redessinées."""

    def __init__(self, zone, tileset, vide=None):
        self.zone, self.ts = zone, tileset
        self.statique = pygame.Surface((zone.w * T, zone.h * T))
        self.anim = []
        rng = random.Random(zone.w * 31 + zone.h)
        pal = px.PALETTES[zone.pal]
        var = tileset.get("var", {})

        def choisir(t, x, y):
            if t in var:
                v = var[t]
                return v[(x * 73856093 ^ y * 19349663) % len(v)]
            return tileset[t][0]

        for y in range(zone.h):
            for x in range(zone.w):
                t = zone.tuiles[y][x]
                if t in ANIMEES:
                    self.anim.append((x, y, t))
                    self.statique.blit(choisir(SOL, x, y) if t != EAU else tileset[EAU][0], (x * T, y * T))
                else:
                    self.statique.blit(choisir(t, x, y), (x * T, y * T))
        # ombre portée douce sous les murs / toits
        ombre = pygame.Surface((T, 4), pygame.SRCALPHA)
        ombre.fill((0, 0, 0, 60))
        for y in range(zone.h - 1):
            for x in range(zone.w):
                if zone.tuiles[y][x] in (MUR, TOIT, FACADE) and zone.tuiles[y + 1][x] not in SOLIDES:
                    self.statique.blit(ombre, (x * T, (y + 1) * T))
        cote = pygame.Surface((3, T), pygame.SRCALPHA)
        for i in range(3):
            pygame.draw.line(cote, (0, 0, 0, 46 - i * 16), (i, 0), (i, T))
        cote_d = pygame.transform.flip(cote, True, False)
        for y in range(zone.h):
            for x in range(1, zone.w - 1):
                if zone.tuiles[y][x] in SOLIDES or zone.tuiles[y][x] in ANIMEES:
                    continue
                if zone.tuiles[y][x - 1] in (MUR, TOIT, FACADE, PORTE, TORCHE):
                    self.statique.blit(cote, (x * T, y * T))
                if zone.tuiles[y][x + 1] in (MUR, TOIT, FACADE, PORTE, TORCHE):
                    self.statique.blit(cote_d, (x * T + T - 3, y * T))

    def dessiner(self, surf, cam, temps):
        vue = pygame.Rect(cam[0], cam[1], surf.get_width(), surf.get_height())
        surf.blit(self.statique, (0, 0), vue)
        frame = int(temps * 2.5) % 2
        for x, y, t in self.anim:
            px_, py_ = x * T - cam[0], y * T - cam[1]
            if -T < px_ < surf.get_width() and -T < py_ < surf.get_height():
                surf.blit(self.ts[t][frame if t != HERBE else (int(temps * 1.5 + x * 0.3) % 2)], (px_, py_))


# --------------------------------------------------------------------------------------
# Finalisation d'une zone : boss, coffres, autels, PNJ, lumières
# --------------------------------------------------------------------------------------
def finaliser(z, rng, cfg):
    """cfg : cle, nb_coffres, boss=[numéros], pnjs=[{nom, sprite, role, lignes, slot}], verrou=[numéros de boss requis]."""
    acces = z.slots["acces"]
    z.cle = cfg["cle"]
    z.verrou = list(cfg.get("verrou", []))
    z.prosperite = cfg.get("prosperite", 1)
    z.ambiance = cfg.get("ambiance", (255, 255, 255))
    z.musique = cfg.get("musique", "foret")
    z.musique_combat = "boss" if cfg.get("boss") else "combat"
    bpos = []
    nums = list(cfg.get("boss", []))
    if len(nums) == 2:
        bpos = [z.mid_boss_pos, z.boss_pos]
    elif len(nums) == 1:
        bpos = [z.boss_pos]
    for n, (bx, by) in zip(nums, bpos):
        z.boss.append(dict(x=bx, y=by, num=n))
    reserves = [z.entree_prev, z.entree_next] + bpos
    # autels (soin + sauvegarde) : près de l'entrée et avant le boss
    if cfg.get("autels", z.biome != "village"):
        d0 = distances(z, z.entree_prev)
        cands = [c for c, d in d0.items() if 3 <= d <= 5 and z.tuile(*c) == SOL]
        if bpos:
            d1 = distances(z, bpos[0])
            cands2 = [c for c, d in d1.items() if 8 <= d <= 11 and z.tuile(*c) == SOL]
        else:
            cands2 = []
        for lst in (cands, cands2):
            if lst:
                c = rng.choice(lst)
                z.tuiles[c[1]][c[0]] = AUTEL
                z.autels.append(c)
    for a in z.autels:
        z.lumieres.append((a[0], a[1], 54, (180, 140, 255)))
    # coffres
    pool = z.slots.get("loin") or [c for c in acces]
    for i, c in enumerate(cases_libres(z, pool, rng, cfg.get("nb_coffres", 3), eviter=reserves + list(z.autels), dist_min=7)):
        z.coffres.append(dict(x=c[0], y=c[1], id=f"{z.cle}:{i}"))
    # PNJ
    for p in cfg.get("pnjs", []):
        slot = p.get("slot", "libre")
        if slot == "proche_entree":
            d0 = distances(z, z.entree_prev)
            cand = [c for c, d in d0.items() if 2 <= d <= 4 and z.tuile(*c) == SOL and c not in z.occupes]
        else:
            cand = [c for c in z.slots.get(slot, []) if c not in z.occupes and c not in reserves]
            if not cand:
                cand = [c for c in acces if z.tuile(*c) in (SOL, SUR) and c not in z.occupes]
        if cand:
            c = rng.choice(sorted(cand))
            z.pnjs.append(dict(x=c[0], y=c[1], nom=p["nom"], sprite=p["sprite"], role=p.get("role", "dialogue"), lignes=p["lignes"]))
    for dx, dy, r, col in ((z.entree_prev[0], z.entree_prev[1], 40, (200, 160, 255)), (z.entree_next[0], z.entree_next[1], 40, (200, 160, 255))):
        z.lumieres.append((dx, dy, r, col))
    z.cases_loot = [c for c in acces if z.tuile(*c) in (SOL, HERBE, SUR) and c not in z.occupes and c not in reserves]
    return z
