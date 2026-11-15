"""Scène d'exploration 2D : déplacement case par case, compteur de pas, rencontres aléatoires, PNJ, coffres, autels, boss."""
import math
import random

import pygame

import map as cartes
from assets import pixelart as px
from bot import boss as bot_boss
from bot.equipe import adapter_dialogue
from bot.etat import sauvegarder
from combat.scene_combat import SceneCombat
from exploration.loot_systeme import LootSystem
from exploration.magasin import Magasin
from exploration.pnj import PNJ
from exploration.rencontre_aleatoire import RencontreAleatoire
from HUD import hud
from map import moteur as M

T = 16
DIRS = {(0, -1): "haut", (0, 1): "bas", (-1, 0): "gauche", (1, 0): "droite"}
BIOME_VISUEL = {"village": "ville", "foret": "foret", "donjon": "donjon"}


class Ambiance:
    """Particules d'ambiance en espace écran avec parallaxe : lucioles (forêt), poussière dorée (ville), braises (donjon), éclats (Void)."""

    def __init__(self, zone, rng):
        self.kind = "eclats" if zone.monde == "void" else {"foret": "lucioles", "village": "poussiere", "donjon": "braises"}[zone.biome]
        self.col = {"eclats": (150, 110, 255), "lucioles": (230, 230, 110), "poussiere": (255, 220, 150), "braises": (255, 140, 60)}[self.kind]
        self.n = {"eclats": 34, "lucioles": 22, "poussiere": 30, "braises": 26}[self.kind]
        self.p = [[rng.random() * 480, rng.random() * 270, rng.random() * 6.28, rng.uniform(0.6, 1.3)] for _ in range(self.n)]

    def dessiner(self, surf, cam, t):
        k = self.kind
        for x0, y0, ph, par in self.p:
            if k in ("braises", "eclats"):
                vy = 14 if k == "braises" else 8
                x = (x0 - cam[0] * par + math.sin(t * 0.8 + ph) * 10) % 480
                y = (y0 - cam[1] * par - t * vy * par) % 270
                a = 0.5 + 0.5 * math.sin(t * 2 + ph)
            elif k == "lucioles":
                x = (x0 - cam[0] * par + math.sin(t * 0.5 + ph) * 18) % 480
                y = (y0 - cam[1] * par + math.cos(t * 0.6 + ph) * 12) % 270
                a = max(0.0, math.sin(t * 1.4 + ph * 3))
            else:
                x = (x0 - cam[0] * par + t * 5 * par) % 480
                y = (y0 - cam[1] * par + math.sin(t * 0.7 + ph) * 6) % 270
                a = 0.35 + 0.3 * math.sin(t + ph)
            if a <= 0.05:
                continue
            c = tuple(int(v * a) for v in self.col)
            surf.blit(px.lumiere(5 if k != "poussiere" else 3, c), (int(x) - (5 if k != "poussiere" else 3), int(y) - (5 if k != "poussiere" else 3)), special_flags=pygame.BLEND_RGB_ADD)
            surf.set_at((int(x), int(y)), tuple(min(255, v + 90) for v in c))


class SceneExploration:
    transparente = False

    def __init__(self, jeu, index, entree="prev"):
        self.jeu = jeu
        etat = jeu.etat
        self.index = index
        etat.zone = index
        self.zone = cartes.creer_zone(index, etat.graine)
        z = self.zone
        self.batch = cartes.creer_batch(index, z)
        self.table = cartes.table_loot(index)
        self.rng = random.Random()
        self.loot = LootSystem(self.rng)
        z.boss = [b for b in z.boss if b["num"] not in etat.boss_vaincus]
        self.pnjs = [PNJ(p["nom"], p["sprite"], p["role"], p["lignes"], p["x"], p["y"]) for p in z.pnjs]
        self.rencontre = RencontreAleatoire(BIOME_VISUEL[z.biome] if z.biome != "village" else "ville", z.niveau, z.monde == "void", self.rng)
        self.magasin = Magasin(z, etat.graine, [p.classe_id for p in etat.equipe]) if any(p.role == "marchand" for p in self.pnjs) else None
        if entree == "pos" and etat.pos and etat.zone == index:
            self.x, self.y = etat.pos
        else:
            self.x, self.y = z.entree_prev if entree == "prev" else z.entree_next
        self.dir = "droite" if entree == "prev" else "gauche"
        self.mouv = None                 # (cible_x, cible_y, progression)
        self.trail = [(self.x, self.y)] * 5
        self.temps = 0.0
        self.dialogue = None
        self.apres_dialogue = None
        self.fade = 1.0
        self.banniere = 3.0
        self.sol = []
        self.sol_vu = 0
        self.remplir_sol(self.loot.nombre_sol(self.table.SOL_NB, etat.victoires))
        self.interactif = None
        self.pas_son = 0
        self.invincible = 4          # pas sans rencontre à l'arrivée
        self.rencontre.pas_depuis = -4
        jeu.audio.musique(z.musique)
        etat.pos = (self.x, self.y)
        sauvegarder(etat)
        self.cache_ombre = None
        self.ambiance_fx = Ambiance(z, self.rng)
        self.vision = 0.0           # Vision des ténèbres (secondes restantes)
        self.regard = 0.0           # Regard du Vide
        self.furtif_pas = 0         # Marche d'ombre (pas restants)

    # ------------------------------------------------------------------ contenu
    def remplir_sol(self, n):
        z, etat = self.zone, self.jeu.etat
        libres = [c for c in z.cases_loot if abs(c[0] - self.x) + abs(c[1] - self.y) > 4 and not any((s["x"], s["y"]) == c for s in self.sol)]
        self.rng.shuffle(libres)
        classes = [p.classe_id for p in etat.equipe]
        for c in libres[:max(0, n - len(self.sol))]:
            r = self.loot.rarete_sol(self.table.SOL_POIDS, etat.victoires)
            self.sol.append(dict(x=c[0], y=c[1], objet=self.loot.objet(r, classes)))

    def coffre_ouvert(self, c):
        return c["id"] in self.jeu.etat.coffres

    def entite_en(self, x, y):
        for p in self.pnjs:
            if (p.x, p.y) == (x, y):
                return ("pnj", p)
        for b in self.zone.boss:
            if (b["x"], b["y"]) == (x, y):
                return ("boss", b)
        for c in self.zone.coffres:
            if (c["x"], c["y"]) == (x, y):
                return ("coffre", c)
        if self.zone.tuile(x, y) == M.AUTEL:
            return ("autel", (x, y))
        return None

    def verrou_actif(self):
        return any(n not in self.jeu.etat.boss_vaincus for n in self.zone.verrou)

    def bloque(self, x, y):
        z = self.zone
        t = z.tuile(x, y)
        if t in M.SOLIDES or self.entite_en(x, y):
            return True
        return False

    # ------------------------------------------------------------------ entrées
    def handle(self, event, jeu):
        a = jeu.clavier.action(event)
        if self.dialogue:
            if a == "valider" or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
                if self.dialogue.valider():
                    self.dialogue = None
                    cb, self.apres_dialogue = self.apres_dialogue, None
                    if cb:
                        cb()
            return
        if a == "menu":
            from HUD.ecrans import SceneMenuPause
            jeu.audio.jouer("valide")
            jeu.pousser(SceneMenuPause(jeu, self))
        elif a == "pouvoir" and not self.mouv:
            from HUD.ecrans import SceneMenuPouvoirs
            jeu.audio.jouer("valide")
            jeu.pousser(SceneMenuPouvoirs(jeu, self))
        elif a == "valider" and not self.mouv:
            self.interagir()

    def parler(self, lignes, apres=None):
        from HUD.hud import Dialogue
        self.dialogue = Dialogue(lignes)
        self.apres_dialogue = apres

    def interagir(self):
        dx, dy = next(k for k, v in DIRS.items() if v == self.dir)
        e = self.entite_en(self.x + dx, self.y + dy)
        if not e:
            return
        kind, obj = e
        jeu, etat = self.jeu, self.jeu.etat
        if kind == "pnj":
            obj.regarder((self.x, self.y))
            d = obj.dialoguer({"boss_vaincus": len(etat.boss_vaincus)})
            self.dialogue = d
            if obj.role == "marchand" and self.magasin:
                from HUD.ecrans import SceneBoutique
                self.apres_dialogue = lambda: jeu.pousser(SceneBoutique(jeu, self.magasin))
        elif kind == "coffre":
            self.ouvrir_coffre(obj)
        elif kind == "autel":
            for p in etat.equipe:
                p.soigner_complet()
            etat.pos = (self.x, self.y)
            ok = sauvegarder(etat)
            jeu.audio.jouer("autel")
            jeu.notif.ajouter("L'Outsider vous observe... Groupe soigné" + (" - partie sauvegardée" if ok else ""), hud.VIOLET, 3.2)
            self.fade = -0.6
        elif kind == "boss":
            self.declencher_boss(obj)

    def ouvrir_coffre(self, c):
        etat = self.jeu.etat
        if self.coffre_ouvert(c):
            self.jeu.notif.ajouter("Le coffre est vide.", hud.GRIS)
            return
        etat.coffres.add(c["id"])
        objets, gold = self.loot.butin_coffre(self.table.COFFRE_RARETE, [p.classe_id for p in etat.equipe])
        etat.or_ += int(gold)
        self.jeu.audio.jouer("ouvre")
        for o in objets:
            etat.sac.ajouter(o)
            self.jeu.notif.ajouter(f"Coffre : {o.nom} ({px.RARETE_NOMS[o.rarete]})", px.RARETE_COULEURS[o.rarete], 2.6)
        self.jeu.notif.ajouter(f"+{int(gold)} or", hud.OR, 2.0)

    # ------------------------------------------------------------------ combats
    def lancer_combat(self, ennemis, boss_num=None):
        z = self.zone
        sc = SceneCombat(self.jeu, ennemis, BIOME_VISUEL[z.biome], z.monde, boss_num, fin=self.apres_combat)
        self.jeu.pousser(sc)

    def declencher_boss(self, b):
        info = bot_boss.infos(b["num"])
        rng = random.Random()
        self.parler(adapter_dialogue(info["intro"], self.jeu.etat.equipe), lambda: self.lancer_combat([bot_boss.creer_boss(b["num"], rng)], b["num"]))

    def apres_combat(self, res):
        etat = self.jeu.etat
        if res is None:
            return
        if res["etat"] == "fuite":
            self.rencontre.pas_depuis = -6
            return
        etat.victoires += 1
        self.rencontre.pas_depuis = -3
        if res.get("boss"):
            n = res["boss"]
            etat.boss_vaincus.add(n)
            etat.runes.append(n)
            self.zone.boss = [b for b in self.zone.boss if b["num"] != n]
            self.jeu.notif.ajouter(f"Rune Interdite récupérée ({len(etat.runes)}/6)", hud.VIOLET, 3.5)
            info = bot_boss.infos(n)
            if n == 6:
                from HUD.ecrans import SceneFin
                self.parler(adapter_dialogue(info["outro"], etat.equipe), lambda: self.jeu.reinitialiser(SceneFin(self.jeu)))
            else:
                self.parler(adapter_dialogue(info["outro"], etat.equipe))
        else:
            if etat.victoires % 2 == 0:       # le taux de loot au sol augmente avec les victoires
                self.remplir_sol(len(self.sol) + 1)
        self.jeu.audio.musique(self.zone.musique)

    def reprendre(self, jeu):
        jeu.audio.musique(self.zone.musique)

    # ------------------------------------------------------------------ mise à jour
    def update(self, dt, jeu):
        self.temps += dt
        self.banniere = max(0, self.banniere - dt)
        self.vision = max(0.0, self.vision - dt)
        self.regard = max(0.0, self.regard - dt)
        self.fade = self.fade - dt * 1.8 if self.fade > 0 else min(0, self.fade + dt * 1.8)
        if self.dialogue:
            self.dialogue.update(dt)
            return
        z = self.zone
        etat = jeu.etat
        etat.temps += dt
        if self.mouv:
            tx, ty, p = self.mouv
            vit = 9.0 if jeu.clavier.maintenu("courir") else 5.5
            p += dt * vit
            if p >= 1.0:
                self.finir_pas(tx, ty)
            else:
                self.mouv = (tx, ty, p)
            return
        dx, dy = jeu.clavier.direction()
        if dx and dy:
            dy = 0 if DIRS.get((dx, 0)) != self.dir else dy
            dx = 0 if dy else dx
        if dx or dy:
            self.dir = DIRS[(dx, dy)]
            tx, ty = self.x + dx, self.y + dy
            e = self.entite_en(tx, ty)
            t = z.tuile(tx, ty)
            if e and e[0] == "boss":
                self.declencher_boss(e[1])
            elif t == M.SORTIE_NEXT and self.verrou_actif():
                if not getattr(self, "_msg_t", 0) > self.temps:
                    jeu.notif.ajouter("Une force scelle cette issue. Un Gardien veille encore...", hud.ROUGE, 2.5)
                    self._msg_t = self.temps + 2.5
            elif t == M.SORTIE_NEXT and self.index == len(cartes.ORDRE) - 1:
                pass
            elif t == M.SORTIE_PREV and self.index == 0:
                if not getattr(self, "_msg_t", 0) > self.temps:
                    jeu.notif.ajouter("Il n'y a plus de retour possible : le Guet vous traque.", hud.GRIS, 2.2)
                    self._msg_t = self.temps + 2.2
            elif not self.bloque(tx, ty):
                self.mouv = (tx, ty, 0.0)
        # cible d'interaction
        ddx, ddy = next(k for k, v in DIRS.items() if v == self.dir)
        e = self.entite_en(self.x + ddx, self.y + ddy)
        self.interactif = e

    def finir_pas(self, tx, ty):
        jeu, etat, z = self.jeu, self.jeu.etat, self.zone
        self.mouv = None
        self.x, self.y = tx, ty
        self.trail.insert(0, (tx, ty))
        self.trail = self.trail[:6]
        etat.pas_total += 1
        etat.pos = (tx, ty)
        self.pas_son += 1
        if self.pas_son % 2 == 0:
            jeu.audio.jouer("pas")
        t = z.tuile(tx, ty)
        if t == M.SORTIE_NEXT and self.index < len(cartes.ORDRE) - 1:
            jeu.changer(SceneExploration(jeu, self.index + 1, "prev"))
            return
        if t == M.SORTIE_PREV and self.index > 0:
            jeu.changer(SceneExploration(jeu, self.index - 1, "next"))
            return
        for s in list(self.sol):
            if (s["x"], s["y"]) == (tx, ty):
                self.sol.remove(s)
                etat.sac.ajouter(s["objet"])
                jeu.audio.jouer("objet")
                o = s["objet"]
                jeu.notif.ajouter(f"Ramassé : {o.nom}", px.RARETE_COULEURS[o.rarete], 2.0)
        self.furtif_pas = max(0, self.furtif_pas - 1)
        if t != M.SUR and (self.furtif_pas <= 0 or self.rng.random() < 0.25) and self.rencontre.pas(t == M.HERBE):
            self.lancer_combat(self.rencontre.composer())

    # ------------------------------------------------------------------ rendu
    def cam(self):
        z = self.zone
        px_, py_ = self.x * T + 8, self.y * T + 8
        if self.mouv:
            tx, ty, p = self.mouv
            px_ += (tx - self.x) * T * p
            py_ += (ty - self.y) * T * p
        cx = max(0, min(z.w * T - 480, px_ - 240))
        cy = max(0, min(z.h * T - 270, py_ - 135))
        if z.w * T < 480:
            cx = -(480 - z.w * T) / 2
        if z.h * T < 270:
            cy = -(270 - z.h * T) / 2
        return int(cx), int(cy)

    def sprite_pos(self, i):
        """Position écran (en pixels monde) du membre i du groupe : le meneur suit son déplacement, les autres la piste."""
        if i == 0:
            x, y = self.x * T, self.y * T
            if self.mouv:
                tx, ty, p = self.mouv
                x += (tx - self.x) * T * p; y += (ty - self.y) * T * p
            return x, y
        a = self.trail[i - 1] if i - 1 < len(self.trail) else self.trail[-1]
        b = self.trail[i] if i < len(self.trail) else self.trail[-1]
        p = self.mouv[2] if self.mouv else 0
        if not self.mouv:
            return a[0] * T, a[1] * T
        return (b[0] + (a[0] - b[0]) * p) * T, (b[1] + (a[1] - b[1]) * p) * T

    def draw(self, surf, jeu):
        z, etat = self.zone, jeu.etat
        cam = self.cam()
        surf.fill((0, 0, 0))
        self.batch.dessiner(surf, cam, self.temps)
        ents = []
        for s in self.sol:
            ents.append((s["y"] * T, "sol", s))
        for c in z.coffres:
            ents.append((c["y"] * T, "coffre", c))
        for p in self.pnjs:
            ents.append((p.y * T, "pnj", p))
        for b in z.boss:
            ents.append((b["y"] * T, "boss", b))
        n = len(etat.equipe)
        for i in range(n - 1, -1, -1):
            sx, sy = self.sprite_pos(i)
            ents.append((sy, "joueur", (i, sx, sy)))
        ents.sort(key=lambda e: e[0])
        marche = 1 if self.mouv else 0
        for _, kind, o in ents:
            if kind == "sol":
                bob = int(math.sin(self.temps * 3 + o["x"]) * 2)
                x, y = o["x"] * T - cam[0], o["y"] * T - cam[1]
                lum = px.lumiere(10, px.RARETE_COULEURS[o["objet"].rarete])
                surf.blit(lum, (x - 2, y - 2), special_flags=pygame.BLEND_RGB_ADD)
                surf.blit(o["objet"].icone, (x + 1, y + 1 + bob))
            elif kind == "coffre":
                surf.blit(px.coffre(self.coffre_ouvert(o), 3), (o["x"] * T - cam[0], o["y"] * T - cam[1]))
            elif kind == "pnj":
                self.ombre_pied(surf, o.x * T - cam[0] + 8, o.y * T - cam[1] + 15)
                img = px.chibi(o.sprite, o.dir, 0, 1)
                surf.blit(img, (o.x * T - cam[0] - 1, o.y * T - cam[1] - 11))
                if self.interactif and self.interactif[1] is o and int(self.temps * 3) % 2:
                    hud.texte(surf, "!", (o.x * T - cam[0] + 8, o.y * T - cam[1] - 22), hud.OR, 16, centre=True)
            elif kind == "boss":
                info = bot_boss.infos(o["num"])
                img = px.boss(info["sprite"], 2, int(self.temps * 2) % 2)
                x, y = o["x"] * T - cam[0] + 8, o["y"] * T - cam[1] + 16
                lum = px.lumiere(30, (160, 60, 220) if z.monde == "void" else (200, 90, 60))
                surf.blit(lum, (x - 30, y - 50), special_flags=pygame.BLEND_RGB_ADD)
                surf.blit(img, img.get_rect(midbottom=(x, y + int(math.sin(self.temps * 2) * 2))))
            else:
                i, sx, sy = o
                self.ombre_pied(surf, sx - cam[0] + 8, sy - cam[1] + 15)
                p = etat.equipe[i]
                frame = (1 if (self.mouv and self.mouv[2] < 0.5) else 3) if self.mouv else 0
                d = self.dir if i == 0 else self.dir_suiveur(i)
                img = px.chibi(p.classe.sprite, d, frame, 1, espece=p.espece)
                surf.blit(img, (sx - cam[0] - 1, sy - cam[1] - 11))
        self.eclairage(surf, cam)
        if self.jeu.conf["graphismes"].get("ambiance", True):
            self.ambiance_fx.dessiner(surf, cam, self.temps)
            surf.blit(px.vignette(130 if min(self.zone.ambiance) > 150 else 170), (0, 0))
        self.dessiner_vision(surf, cam)
        self.interface(surf)
        if self.fade != 0:
            v = pygame.Surface((480, 270)); v.fill((0, 0, 0) if self.fade > 0 else (200, 170, 255))
            v.set_alpha(int(255 * min(1, abs(self.fade)))); surf.blit(v, (0, 0))
        if self.dialogue:
            self.dialogue.dessiner(surf)

    def teleporter(self, case):
        self.x, self.y = case
        self.mouv = None
        self.trail = [case] * 6
        self.jeu.etat.pos = case
        self.fade = -0.35

    def dessiner_vision(self, surf, cam):
        """Vision des ténèbres / Regard du Vide : tout ce qui est caché derrière les murs brille."""
        if self.vision <= 0 and self.regard <= 0:
            return
        a = min(1.0, max(self.vision, self.regard) / 1.5)
        ov = pygame.Surface((480, 270), pygame.SRCALPHA)
        ov.fill((10, 20, 70, int(95 * a)) if self.vision > 0 else (45, 10, 70, int(80 * a)))
        surf.blit(ov, (0, 0))
        z = self.zone
        marques = []
        if self.vision > 0:
            marques += [(p.x, p.y, (120, 255, 140), 6) for p in self.pnjs]
            marques += [(s["x"], s["y"], px.RARETE_COULEURS[s["objet"].rarete], 5) for s in self.sol]
        marques += [(c["x"], c["y"], (255, 215, 90), 6) for c in z.coffres if not self.coffre_ouvert(c)]
        marques += [(b["x"], b["y"], (255, 70, 90) if self.vision > 0 else (215, 110, 255), 7 if self.vision > 0 else 11) for b in z.boss]
        for x, y, col, r in marques:
            sx, sy = x * T - cam[0] + 8, y * T - cam[1] + 8
            rr = int(r * 2 * (1 + 0.25 * math.sin(self.temps * 5)))
            surf.blit(px.lumiere(rr, col), (sx - rr, sy - rr), special_flags=pygame.BLEND_RGB_ADD)
            pygame.draw.circle(surf, col, (sx, sy), 2)
        if self.regard > 0 and z.boss:
            b = min(z.boss, key=lambda b: abs(b["x"] - self.x) + abs(b["y"] - self.y))
            ang = math.atan2(b["y"] - self.y, b["x"] - self.x)
            cx, cy = 240, 135
            pointe = (cx + math.cos(ang) * 70, cy + math.sin(ang) * 70)
            g = (cx + math.cos(ang + 2.6) * 52, cy + math.sin(ang + 2.6) * 52)
            d = (cx + math.cos(ang - 2.6) * 52, cy + math.sin(ang - 2.6) * 52)
            pygame.draw.polygon(surf, (215, 110, 255), [pointe, g, (cx + math.cos(ang) * 50, cy + math.sin(ang) * 50), d])
            hud.texte(surf, f"Rune - {abs(b['x'] - self.x) + abs(b['y'] - self.y)} cases", (240, 214), (230, 170, 255), 14, centre=True)

    def ombre_pied(self, surf, x, y):
        if not hasattr(self, "_ombre"):
            self._ombre = pygame.Surface((14, 6), pygame.SRCALPHA)
            pygame.draw.ellipse(self._ombre, (0, 0, 0, 95), (0, 0, 14, 6))
        surf.blit(self._ombre, (int(x) - 7, int(y) - 3))

    def dir_suiveur(self, i):
        a = self.trail[i - 1] if i - 1 < len(self.trail) else self.trail[-1]
        b = self.trail[i] if i < len(self.trail) else self.trail[-1]
        dx, dy = a[0] - b[0], a[1] - b[1]
        if (dx, dy) in DIRS:
            return DIRS[(dx, dy)]
        return self.dir

    def eclairage(self, surf, cam):
        amb = self.zone.ambiance
        if not self.jeu.conf["graphismes"].get("ambiance", True) or amb == (255, 255, 255):
            return
        if self.cache_ombre is None:
            self.cache_ombre = pygame.Surface((480, 270))
        ombre = self.cache_ombre
        ombre.fill(amb)
        for (lx, ly, r, col) in self.zone.lumieres:
            x, y = lx * T + 8 - cam[0], ly * T + 8 - cam[1]
            if -r < x < 480 + r and -r < y < 270 + r:
                f = 1 + math.sin(self.temps * 7 + lx) * 0.05
                rr = int(r * f)
                ombre.blit(px.lumiere(rr, col), (x - rr, y - rr), special_flags=pygame.BLEND_RGB_ADD)
        sx, sy = self.sprite_pos(0)
        rr = 64 if min(amb) < 120 else 90
        ombre.blit(px.lumiere(rr, (255, 240, 215)), (sx + 8 - cam[0] - rr, sy + 8 - cam[1] - rr), special_flags=pygame.BLEND_RGB_ADD)
        surf.blit(ombre, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

    def interface(self, surf):
        etat = self.jeu.etat
        # mini-statut du groupe
        for i, p in enumerate(etat.equipe):
            y = 4 + i * 9
            pygame.draw.rect(surf, (10, 8, 18), (4, y, 62, 8))
            hud.barre(surf, (6, y + 1, 58, 3), p.pv / max(1, p.pv_max), hud.couleur_pv(p.pv / max(1, p.pv_max)), brillance=False)
            hud.barre(surf, (6, y + 5, 58, 2), p.mana / max(1, p.mana_max), (90, 140, 255), brillance=False)
        hud.texte(surf, f"{etat.or_} or", (476, 4), hud.OR, 14, droite=True)
        hud.texte(surf, f"Runes {len(etat.runes)}/6", (476, 16), hud.VIOLET, 14, droite=True)
        if self.banniere > 0:
            a = min(1, self.banniere)
            w = hud.largeur_texte(self.zone.nom, 24) + 40
            hud.fenetre(surf, ((480 - w) // 2, 28, w, 28), alpha=int(230 * a))
            hud.texte(surf, self.zone.nom, (240, 33), hud.OR, 24, centre=True)
        if self.furtif_pas > 0:
            hud.texte(surf, f"Furtif ({self.furtif_pas})", (476, 28), (170, 150, 230), 13, droite=True)
        if self.interactif and not self.dialogue and not self.mouv:
            k = self.interactif[0]
            txt = {"pnj": "Parler", "coffre": "Ouvrir", "autel": "Prier à l'autel", "boss": "Défier"}[k]
            hud.texte(surf, f"Entrée : {txt}", (240, 252), hud.BLANC, 14, centre=True)
