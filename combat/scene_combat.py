"""Scène de combat : rendu, animations et menus (façon Final Fantasy). La logique est dans combat_tour_par_tour.py."""
import math
import random

import pygame

from assets import pixelart as px
from bot import boss as bot_boss
from bot.position import positions_allies, positions_ennemis
from combat import actions as act
from combat.combat_tour_par_tour import Combat
from classe import PASSIFS
from exploration.loot_systeme import LootSystem
from exploration.objets import groupes
from HUD import hud

DUREES_FX = dict(rafale=0.55, rats=0.65, invocation=0.65, possession=0.55, coup=0.34, tir=0.34, explosion=0.62, blink=0.46, attriction=0.55, temps=0.9, domino=0.6, soin=0.5, buff=0.55, garde=0.4)
VIOLET = (170, 100, 255)


class SceneCombat:
    transparente = False

    def __init__(self, jeu, ennemis, biome, monde, boss_num=None, fin=None, zone_loot=None):
        self.jeu, self.fin_cb, self.boss_num, self.zone_loot = jeu, fin, boss_num, zone_loot
        etat = jeu.etat
        self.rng = random.Random()
        self.allies = [p.en_combattant() for p in etat.equipe]
        self.ennemis = ennemis
        self.combat = Combat(self.allies, ennemis, etat.sac.objets, bool(boss_num), self.rng)
        self.fond = px.fond_combat(biome, monde)
        self.pos = {}
        for c, p in zip(self.allies, positions_allies(len(self.allies))):
            self.pos[c] = p
        for c, p in zip(ennemis, positions_ennemis(len(ennemis), bool(boss_num))):
            self.pos[c] = p
        self.t = 0.0
        self.etincelles = []
        self.mode = "intro"
        self.queue, self.attente, self.fx, self.suite = [], 0.0, [], "prochain"
        self.flottants = hud.Flottants()
        self.acteur = None
        self.menu = None
        self.action = {}
        self.aide = ""
        self.bandeau = ("", 0)
        self.shake = 0.0
        self.vitesse = 1.0
        self.cible_i = 0
        self.cibles = []
        self.resultats = None
        self.intro_t = 0.0
        self.particules = [[self.rng.random() * 480, self.rng.random() * 270, self.rng.random() * 6.28] for _ in range(34)]
        self.monde = monde
        noms = {}
        for e in ennemis:
            noms[e.nom.rstrip(" ABCDE")] = noms.get(e.nom.rstrip(" ABCDE"), 0) + 1
        self.texte_intro = (ennemis[0].nom + " se dresse devant vous !") if boss_num else "Des ennemis surgissent : " + ", ".join(f"{n} x{k}" if k > 1 else n for n, k in noms.items())
        jeu.audio.musique("boss" if boss_num else "combat")

    # ------------------------------------------------------------------ sprites
    def sprite(self, c):
        if c.classe.id == "monstre":
            img = px.monstre(c.variante, c.void, 2, int(self.t * 2.2) % 2)
        elif c.boss:
            img = px.boss(c.sprite, bot_boss.infos(self.boss_num)["echelle"], 0)
        else:
            d = "gauche" if c.allie else "droite"
            esp = getattr(c, "espece", None)
            img = px.chibi(c.sprite, d, 0, 2, True, espece=esp) if esp else px.chibi(c.sprite, d, 0, 2, True)
            if c.void:
                img = px.teinter(img, (150, 170, 255))
        if c.tint:
            img = px.teinter(img, c.tint)
        return img

    def sync_renforts(self):
        """Donne une position aux alliés invoqués (assassin, sosie)."""
        libres = [(318, 128), (318, 196), (300, 162)]
        for r in self.combat.renforts:
            if r not in self.pos:
                utilises = {self.pos[x] for x in self.combat.renforts if x in self.pos}
                self.pos[r] = next((q for q in libres if q not in utilises), (300, 162))

    def dessiner_combattant(self, surf, c):
        x, y = self.pos[c]
        img = self.sprite(c)
        bob = int(math.sin(self.t * 3 + x) * 1.5) if c.vivant else 0
        if not c.vivant:
            c.alpha = max(40 if (c.allie and not c.auto) else 0, c.alpha - 6)
        if c.alpha <= 0:
            return
        if c.flash > 0 or c.alpha < 255:
            img = img.copy()
            if c.flash > 0:
                v = int(200 * min(1, c.flash * 4))
                img.fill((v, v, v, 0), special_flags=pygame.BLEND_RGB_ADD)
            if c.alpha < 255:
                img.set_alpha(c.alpha)
        ox, oy = c.offset
        r = img.get_rect(midbottom=(x + ox, y + bob + oy + (0 if c.vivant else 6)))
        ombre = pygame.Surface((r.w, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(ombre, (0, 0, 0, 90), (r.w * 0.1, 0, r.w * 0.8, 8))
        surf.blit(ombre, (r.x, y - 4))
        surf.blit(img, r)
        if not c.vivant:
            return
        # pastilles d'état
        px0, py0 = r.centerx - 8, r.y - 7
        k = 0
        for alt in c.rang.liste:
            pygame.draw.rect(surf, hud.VERT if alt.positif else hud.ROUGE, (px0 + k * 5, py0, 4, 4)); k += 1
        if c.en_defense:
            pygame.draw.rect(surf, hud.BLEU, (px0 + k * 5, py0, 4, 4)); k += 1
        if c.lien is not None:
            pygame.draw.rect(surf, VIOLET, (px0 + k * 5, py0, 4, 4))
        if not c.allie:   # mini-barre de PV ennemie
            hud.barre(surf, (r.centerx - 14, y + 2, 28, 3), c.pv_aff / max(1, c.pv.maximum), hud.couleur_pv(c.pv.ratio))

    # ------------------------------------------------------------------ événements
    def pousser(self, evs):
        self.queue.extend(evs)

    def centre(self, c):
        x, y = self.pos[c]
        return (x, y - 24)

    def appliquer(self, e):
        t = e["t"]
        self.sync_renforts()
        a = 0.0
        if t == "annonce":
            self.bandeau = (e["texte"], 1.1); a = 0.55
        elif t == "texte":
            self.bandeau = (e["texte"], 1.3); a = 0.7
        elif t == "anim":
            d = DUREES_FX.get(e["fx"], 0.4)
            self.fx.append(dict(fx=e["fx"], t=0.0, d=d, src=e["acteur"], cibles=list(e["cibles"])))
            snd = {"coup": "coup", "tir": "tir", "explosion": "explosion", "blink": "blink", "attriction": "magie", "temps": "temps",
                   "domino": "magie", "soin": "soin", "buff": "soin", "garde": "valide", "rafale": "blink", "rats": "explosion"}.get(e["fx"], "magie")
            self.jeu.audio.jouer(snd)
            a = d
        elif t == "degats":
            c = e["cible"]
            n = e["n"]
            coul = hud.JAUNE if e["crit"] else (VIOLET if e["nature"] == "mag" else (hud.BLEU if e["nature"] == "brut" else hud.BLANC))
            self.flottants.ajouter(("CRITIQUE " if e["crit"] else "") + str(n), self.centre(c), coul, 24 if e["crit"] else 20)
            c.flash = 0.3
            cx, cy = self.centre(c)
            col = (255, 235, 140) if e["crit"] else ((200, 140, 255) if e["nature"] == "mag" else ((140, 200, 255) if e["nature"] == "brut" else (255, 255, 255)))
            for _ in range(22 if e["crit"] else 11):
                a = self.rng.uniform(0, 6.283); v = self.rng.uniform(30, 120 if e["crit"] else 80)
                self.etincelles.append([cx, cy, math.cos(a) * v, math.sin(a) * v - 30, self.rng.uniform(0.25, 0.55), col])
            if e["crit"]:
                self.shake = 0.35
                self.jeu.audio.jouer("critique")
            elif e["nature"] == "phys":
                self.shake = max(self.shake, 0.12)
            a = 0.3 if not e["crit"] else 0.45
        elif t == "rate":
            self.flottants.ajouter("Raté", self.centre(e["cible"]), hud.GRIS, 18)
            self.jeu.audio.jouer("rate")
            a = 0.3
        elif t == "soin":
            c = e["cible"]
            self.flottants.ajouter(f"+{e['n']}" + ("" if e["stat"] == "PV" else " MP"), self.centre(c), hud.VERT if e["stat"] == "PV" else hud.BLEU, 20)
            a = 0.35
        elif t == "statut":
            if not e.get("discret"):
                self.flottants.ajouter(e["texte"], (self.centre(e["cible"])[0], self.centre(e["cible"])[1] - 14), hud.VERT if e["positif"] else hud.ROUGE, 15, 1.1, False)
            a = 0.0 if e.get("discret") else 0.22
        elif t == "mort":
            self.jeu.audio.jouer("coup")
            a = 0.3
        elif t == "fige":
            self.flottants.ajouter("Figé", self.centre(e["cible"]), (150, 190, 255), 16, 0.8, False)
            a = 0.25
        self.attente = a

    def maj_fx(self, dt):
        for f in self.fx:
            f["t"] += dt
            if f["fx"] in ("coup", "tir", "blink") and f["src"] in self.pos:
                s = f["src"]
                k = math.sin(math.pi * min(1, f["t"] / f["d"]))
                tgt = f["cibles"][0] if f["cibles"] else None
                if tgt is not None:
                    dx = self.pos[tgt][0] - self.pos[s][0]
                    s.offset[0] = (1 if dx > 0 else -1) * (18 if f["fx"] == "coup" else 4) * k
                    if f["fx"] == "blink":
                        s.alpha = max(60, int(255 - 195 * k))
        gardes = []
        for f in self.fx:
            if f["t"] >= f["d"]:
                f["src"].offset[0] = 0
                if f["src"].vivant:
                    f["src"].alpha = 255
            else:
                gardes.append(f)
        self.fx = gardes

    def dessiner_fx(self, surf):
        for f in self.fx:
            p = f["t"] / f["d"]
            tg = [self.centre(c) for c in f["cibles"] if c in self.pos]
            s = self.centre(f["src"])
            k = f["fx"]
            if k == "coup" and tg:
                x, y = tg[0]
                l = int(34 * min(1, p * 2))
                pygame.draw.line(surf, (255, 255, 255), (x - l // 2, y - l // 2), (x + l // 2, y + l // 2), 3)
                pygame.draw.line(surf, (255, 220, 140), (x - l // 2 + 4, y - l // 2), (x + l // 2 + 4, y + l // 2), 1)
            elif k == "tir" and tg:
                x, y = tg[0]
                q = min(1, p * 3)
                pygame.draw.line(surf, (255, 240, 160), s, (s[0] + (x - s[0]) * q, s[1] + (y - s[1]) * q), 2)
                if p > 0.3:
                    pygame.draw.circle(surf, (255, 255, 255), (int(x), int(y)), int(8 * (1 - p)) + 2)
            elif k == "explosion":
                for (x, y) in tg:
                    rg = int(70 * math.sin(math.pi * min(1, p)))
                    if rg > 2:
                        surf.blit(px.lumiere(rg, (255, 150, 60)), (x - rg, y - rg), special_flags=pygame.BLEND_RGB_ADD)
                    for r, c in ((46, (255, 120, 40)), (30, (255, 200, 80)), (14, (255, 255, 220))):
                        rr = int(r * math.sin(math.pi * min(1, p)) )
                        if rr > 0:
                            pygame.draw.circle(surf, c, (int(x), int(y)), rr)
            elif k == "blink" and tg:
                x, y = tg[0]
                rg = int(46 * math.sin(math.pi * min(1, p)))
                if rg > 2:
                    surf.blit(px.lumiere(rg, (150, 90, 255)), (int(x) - rg, int(y) - rg), special_flags=pygame.BLEND_RGB_ADD)
                q = min(1, p * 1.6)
                for i in range(6):
                    off = (i - 3) * 3
                    pygame.draw.line(surf, VIOLET if i % 2 else (230, 200, 255), (s[0], s[1] + off), (s[0] + (x - s[0]) * q, y + off * (1 - q)), 2)
                if p > 0.5:
                    pygame.draw.circle(surf, (230, 200, 255), (int(x), int(y)), int(24 * (1 - p) * 2))
            elif k == "rafale":
                for i in range(7):
                    y = 50 + i * 22
                    x0 = -60 + p * 600 + i * 12
                    pygame.draw.line(surf, (215, 238, 255), (x0 - 50, y + math.sin(p * 9 + i) * 6), (x0, y), 2)
                    pygame.draw.line(surf, (255, 255, 255), (x0 - 24, y + 1), (x0, y), 1)
            elif k == "rats":
                for (x, y) in tg:
                    for i in range(10):
                        a = p * 11 + i * 0.63
                        r = 22 * (1 - p * 0.3)
                        rx, ry = int(x + math.cos(a) * r), int(y + 6 + math.sin(a * 1.3) * r * 0.5)
                        pygame.draw.circle(surf, (58, 46, 46), (rx, ry), 2)
                        surf.set_at((rx, ry), (255, 60, 60))
            elif k == "invocation":
                for (x, y) in tg:
                    surf.blit(px.lumiere(34, (90, 40, 150)), (int(x) - 34, int(y) - 34), special_flags=pygame.BLEND_RGB_ADD)
                    for i in range(3):
                        pygame.draw.ellipse(surf, (190, 140, 255), (int(x) - 16, int(y) + 20 - int((p + i * 0.3) % 1 * 50), 32, 8), 1)
            elif k in ("attriction", "possession"):
                for (x, y) in tg:
                    surf.blit(px.lumiere(34, (70, 30, 120)), (int(x) - 34, int(y) - 34), special_flags=pygame.BLEND_RGB_ADD)
                    for i in range(8):
                        a = p * 9 + i * 0.8
                        r = 26 * (1 - p * 0.5)
                        pygame.draw.circle(surf, (110, 50, 170), (int(x + math.cos(a) * r), int(y + math.sin(a) * r * 0.7)), 3)
            elif k == "temps":
                cx, cy = 240, 120
                pygame.draw.circle(surf, (170, 200, 255), (cx, cy), int(20 + 180 * p), 2)
                pygame.draw.circle(surf, (120, 160, 255), (cx, cy), int(10 + 120 * p), 1)
                for i in range(12):
                    a = i * math.pi / 6
                    pygame.draw.line(surf, (200, 220, 255), (cx + math.cos(a) * 40, cy + math.sin(a) * 40), (cx + math.cos(a) * 48, cy + math.sin(a) * 48))
                a = p * 12
                pygame.draw.line(surf, (255, 255, 255), (cx, cy), (cx + math.cos(a) * 40, cy + math.sin(a) * 40), 2)
                v = pygame.Surface((480, 270), pygame.SRCALPHA); v.fill((90, 120, 255, int(60 * math.sin(math.pi * p)))); surf.blit(v, (0, 0))
            elif k == "domino" and len(tg) >= 2:
                (x0, y0), (x1, y1) = tg[0], tg[1]
                n = 9
                for i in range(n):
                    q = i / (n - 1)
                    pygame.draw.circle(surf, VIOLET if i % 2 else (230, 200, 255), (int(x0 + (x1 - x0) * q), int(y0 + (y1 - y0) * q + math.sin(q * 6 + p * 8) * 6)), 3, 1)
            elif k == "soin":
                for (x, y) in tg:
                    surf.blit(px.lumiere(28, (40, 120, 60)), (int(x) - 28, int(y) - 28), special_flags=pygame.BLEND_RGB_ADD)
                    for i in range(7):
                        yy = y + 14 - p * 40 + (i % 3) * 5
                        pygame.draw.rect(surf, hud.VERT, (int(x - 14 + i * 5), int(yy), 2, 2))
            elif k == "buff":
                for (x, y) in tg:
                    surf.blit(px.lumiere(28, (120, 100, 30)), (int(x) - 28, int(y) - 28), special_flags=pygame.BLEND_RGB_ADD)
                    pygame.draw.ellipse(surf, hud.OR, (int(x - 14), int(y + 20 - p * 48), 28, 8), 1)
                    pygame.draw.ellipse(surf, (255, 250, 200), (int(x - 10), int(y + 26 - p * 48), 20, 6), 1)
            elif k == "garde":
                x, y = s
                pygame.draw.arc(surf, hud.BLEU, (int(x - 22), int(y - 22), 44, 44), 1.9, 4.4, 2)

    # ------------------------------------------------------------------ cycle de combat
    def update(self, dt, jeu):
        self.t += dt
        for c in self.allies + self.combat.renforts + self.ennemis:
            c.flash = max(0, c.flash - dt)
            for jauge, aff in (("pv", "pv_aff"), ("mana", "mana_aff")):
                cible = getattr(c, jauge).valeur
                cur = getattr(c, aff)
                setattr(c, aff, cur + (cible - cur) * min(1, dt * 6) if abs(cible - cur) > 0.5 else cible)
        self.flottants.update(dt)
        self.shake = max(0, self.shake - dt)
        b, bt = self.bandeau
        self.bandeau = (b, max(0, bt - dt))
        for p in self.particules:
            p[2] += dt
        self.maj_fx(dt)
        for e_ in self.etincelles:
            e_[0] += e_[2] * dt; e_[1] += e_[3] * dt; e_[3] += 220 * dt; e_[4] -= dt
        self.etincelles = [e_ for e_ in self.etincelles if e_[4] > 0]
        vit = self.vitesse * (3.0 if (jeu.clavier.maintenu("courir") or jeu.clavier.maintenu("annuler")) and self.mode in ("file", "ennemi") else 1.0)
        m = self.mode
        if m == "intro":
            self.intro_t += dt
            if self.intro_t == dt:
                jeu.audio.jouer("rencontre")
            if self.intro_t > 1.6:
                self.mode = "prochain"
        elif m == "prochain":
            a, evs = self.combat.suivant()
            self.pousser(evs)
            self.acteur = a
            self.suite = "debut"
            self.mode = "file"
        elif m == "file":
            self.attente -= dt * vit
            if self.attente <= 0:
                if self.queue:
                    self.appliquer(self.queue.pop(0))
                elif not self.fx:
                    self.apres_file()
        elif m == "ennemi":
            self.attente -= dt * vit
            if self.attente <= 0:
                self.tour_ennemi()
        elif m in ("victoire", "defaite"):
            self.attente -= dt
            if self.attente <= 0:
                if m == "victoire":
                    self.preparer_resultats()
                else:
                    from HUD.ecrans import SceneGameOver
                    jeu.reinitialiser(SceneGameOver(jeu))

    def apres_file(self):
        c = self.combat
        if c.etat != "en_cours" and self.mode == "file":
            return self.terminer()
        if self.acteur is None:
            return self.terminer()
        s = self.suite
        if s == "debut":
            if self.acteur.allie and not self.acteur.auto:
                self.ouvrir_menu_principal()
            else:
                self.mode = "ennemi"; self.attente = 0.45
        elif s == "menu":
            self.ouvrir_menu_principal()
        else:
            self.mode = "prochain"

    def tour_ennemi(self):
        a = self.acteur
        try:
            obj, action = a.ia(self.combat, a)
            evs = []
            if obj:
                evs += self.combat.utiliser_objet(a, obj[0], obj[1])
            evs += self.combat.executer(a, action)
        except Exception:     # filet de sécurité : l'IA ne doit jamais bloquer le combat
            evs = self.combat.executer(a, {"type": "attaquer", "arme": "melee", "cible": self.combat.adversaires(a)[0]})
        self.pousser(evs)
        self.suite = "prochain"
        self.mode = "file"

    # ------------------------------------------------------------------ menus du joueur
    def ouvrir_menu_principal(self):
        a = self.acteur
        items = ["Objet", "Attaquer", "Magie", "Défendre", "Fuir"]
        off = set()
        if a.objet_utilise or not any(o.type == "conso" for o in self.jeu.etat.sac.objets):
            off.add(0)
        if not a.sorts:
            off.add(2)
        if not self.combat.fuite_possible:
            off.add(4)
        self.menu = hud.Menu(items, largeur=70, visibles=5, taille=15, desactives=off, hauteur_ligne=12)
        self.mode = "menu"
        self.aide = "Phase d'objet optionnelle, puis une action principale."

    def sous_menu(self, genre):
        a = self.acteur
        if genre == "attaquer":
            items, self.ids = [], []
            for arme in a.classe.equipement:
                cout = act.cout_arme(a, arme)
                items.append({"melee": "Arme", "pistolet": "Pistolet", "grenade": f"Grenade ({cout} MP)"}[arme]); self.ids.append(arme)
            off = {i for i, arme in enumerate(self.ids) if not act.peut(a, arme)}
        elif genre == "magie":
            items, self.ids = [], list(a.sorts)
            for s in a.sorts:
                sp = act.SORTS[s]
                items.append(f"{sp.nom} ({a.cout_sort(sp)} MP)")
            off = {i for i, s in enumerate(self.ids) if a.mana.valeur < a.cout_sort(act.SORTS[s])}
        else:
            gr = [(o, n) for o, n in groupes(self.jeu.etat.sac.objets) if o.type == "conso"]
            items = [f"{o.nom} x{n}" for o, n in gr]
            self.ids = [o for o, n in gr]
            off = set()
        self.menu_sous = hud.Menu(items, largeur=150, visibles=5, taille=15, desactives=off, hauteur_ligne=12)
        self.genre = genre
        self.mode = "sous"
        self.aide = self.description_sous()

    def demander_cible(self, liste, suivant, morts=False):
        self.cibles = list(liste) if morts else [c for c in liste if c.vivant]
        if not self.cibles:
            return
        self.cible_i = 0
        self.suivant_cible = suivant
        self.mode = "cible"

    def valider_menu_principal(self, i):
        a = self.acteur
        if i == 0:
            self.sous_menu("objet")
        elif i == 1:
            self.sous_menu("attaquer")
        elif i == 2:
            self.sous_menu("magie")
        elif i == 3:
            self.lancer({"type": "defendre"})
        elif i == 4:
            self.lancer({"type": "fuir"})

    def valider_sous(self, i):
        a, c = self.acteur, self.combat
        choix = self.ids[i]
        if self.genre == "attaquer":
            if choix == "grenade":
                self.lancer({"type": "attaquer", "arme": "grenade"})
            else:
                self.demander_cible(c.adversaires(a), lambda t: self.lancer({"type": "attaquer", "arme": choix, "cible": t[0]}))
        elif self.genre == "magie":
            sp = act.SORTS[choix]
            if sp.cible == "ennemi":
                self.demander_cible(c.adversaires(a), lambda t: self.lancer({"type": "magie", "sort": choix, "cibles": t}))
            elif sp.cible == "deux_ennemis":
                if len(c.adversaires(a)) < 2:
                    self.bandeau = ("Domino exige deux ennemis vivants.", 1.5); self.jeu.audio.jouer("erreur"); return
                self.premiere = None
                self.demander_cible(c.adversaires(a), self.domino_1)
                self.aide = "Domino : choisissez la première cible."
            else:
                self.lancer({"type": "magie", "sort": choix})
        else:
            o = choix
            if "revive" in o.effet:
                morts = [x for x in self.allies if not x.vivant]
                if not morts:
                    self.bandeau = ("Aucun allié à réanimer.", 1.5); self.jeu.audio.jouer("erreur"); return
                self.demander_cible(morts, lambda t: self.utiliser(o, t[0]), morts=True)
            else:
                self.demander_cible(c.amis(a), lambda t: self.utiliser(o, t[0]))
            self.aide = f"{o.nom} : {o.desc}"

    def domino_1(self, t):
        self.premiere = t[0]
        reste = [x for x in self.combat.adversaires(self.acteur) if x is not self.premiere]
        self.aide = "Domino : choisissez la seconde cible."
        self.demander_cible(reste, lambda t2: self.lancer({"type": "magie", "sort": "domino", "cibles": [self.premiere, t2[0]]}))

    def utiliser(self, objet, cible):
        evs = self.combat.utiliser_objet(self.acteur, objet, cible)
        self.pousser(evs)
        self.suite = "menu"
        self.mode = "file"

    def lancer(self, action):
        evs = self.combat.executer(self.acteur, action)
        self.pousser(evs)
        self.suite = "prochain"
        self.mode = "file"

    def handle(self, event, jeu):
        act_ = jeu.clavier.action(event)
        if self.mode == "resultats":
            if act_ == "valider" or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
                self.fermer()
            return
        if self.mode == "menu":
            i = self.menu.traiter(act_, jeu.souris, event)
            if i is not None:
                jeu.audio.jouer("valide"); self.valider_menu_principal(i)
            elif act_ in ("haut", "bas"):
                jeu.audio.jouer("curseur")
        elif self.mode == "sous":
            i = self.menu_sous.traiter(act_, jeu.souris, event)
            if act_ == "annuler":
                jeu.audio.jouer("annule"); self.mode = "menu"
            elif i is not None:
                jeu.audio.jouer("valide"); self.valider_sous(i)
            elif act_ in ("haut", "bas"):
                jeu.audio.jouer("curseur")
                self.aide = self.description_sous()
        elif self.mode == "cible":
            if act_ in ("gauche", "haut"):
                self.cible_i = (self.cible_i - 1) % len(self.cibles); jeu.audio.jouer("curseur")
            elif act_ in ("droite", "bas"):
                self.cible_i = (self.cible_i + 1) % len(self.cibles); jeu.audio.jouer("curseur")
            elif act_ == "annuler":
                jeu.audio.jouer("annule"); self.mode = "sous"
            elif act_ == "valider":
                jeu.audio.jouer("valide"); self.suivant_cible([self.cibles[self.cible_i]])
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, c in enumerate(self.cibles):
                    x, y = self.pos[c]
                    if abs(jeu.souris.pos[0] - x) < 28 and -60 < jeu.souris.pos[1] - y < 8:
                        self.cible_i = i; jeu.audio.jouer("valide"); self.suivant_cible([c]); break

    def description_sous(self):
        i = self.menu_sous.curseur
        if i >= len(self.ids):
            return ""
        if self.genre == "magie":
            return act.SORTS[self.ids[i]].description
        if self.genre == "objet":
            return self.ids[i].desc
        return {"melee": "Dégâts physiques (FOR + arme). Dépend de DEX/AGI.", "pistolet": "Critique garanti s'il touche, mais rate souvent.",
                "grenade": "Dégâts de zone inévitables sur tous les ennemis."}[self.ids[i]]

    # ------------------------------------------------------------------ fin de combat
    def terminer(self):
        c = self.combat
        jeu = self.jeu
        for a in self.allies:
            a.synchroniser_vers_perso()
        if c.etat == "victoire":
            jeu.audio.musique(None); jeu.audio.jouer("victoire")
            self.mode, self.attente = "victoire", 2.0
        elif c.etat == "defaite":
            jeu.audio.musique(None); jeu.audio.jouer("defaite")
            self.mode, self.attente = "defaite", 2.4
        else:   # fuite
            self.mode = "resultats"
            self.resultats = dict(titre="Fuite réussie", lignes=[("Le groupe s'est échappé.", hud.BLANC)], etat="fuite", butin=[])
            self.fermer()

    def preparer_resultats(self):
        etat = self.jeu.etat
        xp, gold, butin = self.combat.recompenses()
        classes = [p.classe_id for p in etat.equipe]
        loot = LootSystem(self.rng)
        butin = list(butin) + loot.butin_ennemi(self.ennemis, classes)
        if self.boss_num:
            from bot.boss import infos
            butin += loot.butin_boss(self.boss_num, infos(self.boss_num)["rarete"], classes)
        lignes = [(f"Expérience +{xp}    Or +{gold}", hud.OR)]
        etat.or_ += gold
        for p in etat.equipe:
            if p.pv <= 0:
                p.pv = 1
            gain = xp if p.pv > 1 or True else xp // 2
            for r in p.gagner_xp(gain):
                g = ", ".join(f"{k} +{v}" for k, v in r["gains"].items())
                lignes.append((f"{p.nom} passe niveau {r['niveau']} !  {g}", hud.VERT))
                for s in r["sorts"]:
                    lignes.append((f"   Nouveau pouvoir : {act.SORTS[s].nom}", hud.VIOLET))
                for pid in r.get("passifs", []):
                    lignes.append((f"   Nouveau passif : {PASSIFS[pid][0]}", hud.VERT))
                self.jeu.audio.jouer("niveau")
        noms = []
        for o in butin:
            etat.sac.ajouter(o)
            noms.append(o)
        self.resultats = dict(titre="VICTOIRE", lignes=lignes, etat="victoire", butin=noms, boss=self.boss_num)
        self.mode = "resultats"

    def fermer(self):
        r = self.resultats
        self.jeu.retour()
        if self.fin_cb:
            self.fin_cb(r)

    # ------------------------------------------------------------------ rendu
    def draw(self, surf, jeu):
        dec = (0, 0)
        if self.shake > 0:
            dec = (random.randint(-3, 3), random.randint(-2, 2))
        scene = pygame.Surface((480, 270))
        scene.blit(self.fond, (0, 0))
        for p in self.particules:       # braises / brume / éclats selon le monde
            x = (p[0] + math.sin(p[2] * 0.7 + p[1]) * 10) % 480
            y = (p[1] - p[2] * (8 if self.monde == "void" else 12)) % 200
            col = (190, 160, 255) if self.monde == "void" else (255, 190, 110)
            scene.set_at((int(x), int(y)), col)
        self.sync_renforts()
        ordre = sorted(self.allies + self.combat.renforts + self.ennemis, key=lambda c: self.pos[c][1])
        if self.mode == "cible":
            self.dessiner_ciblage_dessous(scene)
        for c in ordre:
            self.dessiner_combattant(scene, c)
        liens = [c for c in self.ennemis + self.allies if c.lien is not None and c.vivant and c.lien.vivant]
        for c in liens:
            a, b = self.centre(c), self.centre(c.lien)
            if id(c) < id(c.lien):
                pygame.draw.line(scene, VIOLET, a, b, 1)
        self.dessiner_fx(scene)
        for x, y, _, _, vie, col in self.etincelles:
            k = min(1.0, vie * 3)
            scene.blit(px.lumiere(3, tuple(int(v * k) for v in col)), (int(x) - 3, int(y) - 3), special_flags=pygame.BLEND_RGB_ADD)
            scene.set_at((int(x), int(y)), col)
        brume = pygame.Surface((480, 270), pygame.SRCALPHA)
        for i in range(3):
            bx = (self.t * (6 + i * 3) + i * 170) % 640 - 80
            pygame.draw.ellipse(brume, (200, 190, 230, 14) if self.monde == "void" else (230, 220, 200, 14), (bx - 120, 150 + i * 14, 320, 40))
        scene.blit(brume, (0, 0))
        if self.mode in ("menu", "sous", "cible") and self.acteur is not None:
            ax, ay = self.pos[self.acteur]
            ray = 18 + int(math.sin(self.t * 6) * 2)
            pygame.draw.ellipse(scene, (255, 225, 110), (ax - ray, ay - 6, ray * 2, 12), 1)
            scene.blit(px.lumiere(26, (90, 70, 20)), (ax - 26, ay - 26), special_flags=pygame.BLEND_RGB_ADD)
        scene.blit(px.vignette(140), (0, 0))
        self.flottants.dessiner(scene)
        if self.mode == "cible":
            c = self.cibles[self.cible_i]
            x, y = self.pos[c]
            h = self.sprite(c).get_height()
            hud.curseur_main(scene, (x - 4, y - h - 14 + int(math.sin(self.t * 8) * 2)))
            hud.fenetre(scene, (150, 8, 180, 22))
            hud.texte(scene, f"{c.nom}  {c.pv.valeur}/{c.pv.maximum}", (240, 13), hud.OR, 15, centre=True)
        surf.blit(scene, dec)
        self.dessiner_interface(surf)
        if self.mode == "intro":
            p = self.intro_t
            if p < 0.5:
                v = pygame.Surface((480, 270)); v.fill((255, 255, 255)); v.set_alpha(int(255 * (1 - p / 0.5))); surf.blit(v, (0, 0))
            hud.fenetre(surf, (60, 100, 360, 36))
            hud.texte(surf, self.texte_intro, (240, 112), hud.BLANC, 16, centre=True)
        if self.mode in ("victoire",):
            hud.titre(surf, "VICTOIRE", 90, hud.OR, 44)
        if self.mode == "defaite":
            v = pygame.Surface((480, 270)); v.fill((0, 0, 0)); v.set_alpha(min(255, int(255 * (1 - self.attente / 2.4)))); surf.blit(v, (0, 0))
        if self.mode == "resultats":
            self.dessiner_resultats(surf)

    def dessiner_ciblage_dessous(self, scene):
        c = self.cibles[self.cible_i]
        x, y = self.pos[c]
        pygame.draw.ellipse(scene, (255, 230, 120), (x - 22, y - 6, 44, 12), 1)

    def dessiner_interface(self, surf):
        # bandeau d'annonce
        b, bt = self.bandeau
        if bt > 0 and self.mode not in ("cible",):
            w = hud.largeur_texte(b, 16) + 24
            hud.fenetre(surf, ((480 - w) // 2, 8, w, 22))
            hud.texte(surf, b, (240, 13), hud.BLANC, 16, centre=True)
        elif self.mode in ("menu", "sous") and self.aide:
            w = min(440, hud.largeur_texte(self.aide, 14) + 20)
            hud.fenetre(surf, ((480 - w) // 2, 6, w, 20))
            hud.texte(surf, self.aide, (240, 11), hud.BLANC, 14, centre=True)
        # fenêtre de commandes (gauche) et d'état du groupe (droite)
        hud.fenetre(surf, (4, 200, 236, 66))
        hud.fenetre(surf, (244, 200, 232, 66))
        if self.mode == "menu":
            self.menu.dessiner(surf, (16, 205), cadre=False)
        elif self.mode in ("sous", "cible"):
            self.menu.dessiner(surf, (16, 205), actif=False, cadre=False)
            if self.mode == "sous":
                self.menu_sous.dessiner(surf, (92, 205), cadre=False)
            else:
                self.menu_sous.dessiner(surf, (92, 205), actif=False, cadre=False)
        else:
            noms = {}
            for e in self.ennemis:
                if e.vivant:
                    noms[e.nom] = e
            y = 206
            for i, e in enumerate(list(noms.values())[:5]):
                hud.texte(surf, e.nom, (14 + (i // 3) * 110, 206 + (i % 3) * 14), hud.BLANC, 14)
        for i, c in enumerate(self.allies):
            y = 205 + i * 15
            actif = c is self.acteur and self.mode in ("menu", "sous", "cible")
            if actif:
                pygame.draw.rect(surf, (60, 90, 160), (249, y - 1, 222, 14))
            col = hud.GRIS if not c.vivant else (hud.OR if actif else hud.BLANC)
            hud.texte(surf, c.nom, (254, y), col, 14)
            hud.barre(surf, (306, y + 2, 70, 5), c.pv_aff / max(1, c.pv.maximum), hud.couleur_pv(c.pv.ratio))
            hud.texte(surf, f"{c.pv.valeur}", (428, y), col, 14, droite=True)
            hud.barre(surf, (434, y + 2, 32, 5), c.mana_aff / max(1, c.mana.maximum), (90, 140, 255))

    def dessiner_resultats(self, surf):
        r = self.resultats
        h = 60 + 14 * len(r["lignes"]) + (14 * (len(r["butin"]) + 1) if r["butin"] else 0)
        h = min(h, 230)
        rect = pygame.Rect(50, (270 - h) // 2, 380, h)
        hud.fenetre(surf, rect)
        hud.texte(surf, r["titre"], (240, rect.y + 8), hud.OR, 24, centre=True)
        y = rect.y + 32
        for txt, col in r["lignes"][:9]:
            hud.texte(surf, txt, (rect.x + 14, y), col, 15); y += 14
        if r["butin"]:
            hud.texte(surf, "Butin :", (rect.x + 14, y + 2), hud.OR, 15); y += 16
            for o in r["butin"][:8]:
                surf.blit(o.icone, (rect.x + 18, y - 2))
                hud.texte(surf, o.nom, (rect.x + 36, y), px.RARETE_COULEURS[o.rarete], 15); y += 13
        if int(self.t * 2) % 2 == 0:
            hud.texte(surf, "Entrée pour continuer", (rect.right - 12, rect.bottom - 16), hud.GRIS, 13, droite=True)
