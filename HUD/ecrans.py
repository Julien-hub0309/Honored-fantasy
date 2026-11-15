"""Écrans et menus du jeu : titre, choix d'équipe, intro, pause (statut / objets / équipement), boutique, game over, fin."""
import math
import random

import pygame

import classe as registre
from assets import pixelart as px
from bot import equipe as bot_equipe
from bot.etat import EtatJeu, charger, existe, sauvegarder
from combat import actions as act
from exploration.objets import groupes
from exploration.revente import prix_revente
from HUD import hud

TEXTE_INTRO = [
    "Sur le continent de Pendysia, la brume sent l'huile de baleine et la peste.\nLe Void, le Grand Vide, saigne dans la réalité par une faille que personne ne sait refermer.",
    "Un homme, jadis porteur de la Marque de l'Outsider, rassemble les Runes Interdites.\nIl veut usurper la place de l'Outsider dans le Void.",
    "Le Guet a trouvé ses sacrifiés : un capybara, un panda, un renard et un loup, condamnés à mort.\nTraquez l'Antagoniste, tuez-le, et votre peine sera effacée.\nÉchouez... et la corde reprendra son dû.",
]
TEXTE_FIN = [
    "Lord Vaerith s'effondre. Les six Runes Interdites s'embrasent dans vos mains, puis s'élèvent, l'une après l'autre.",
    "La faille se referme avec un cri de verre. Le Void se retire, laissant un ciel vide et propre sur Pendysia.",
    "Quelque part, l'Outsider sourit. Il garde sa place... et note vos noms.",
    "Les condamnés ne seront jamais pardonnés. Mais, ce soir, la brume sent presque la pluie.",
]


def fond_brume(surf, t, monde="void"):
    surf.blit(px.fond_combat("ville", monde), (0, 0))
    v = pygame.Surface((480, 270), pygame.SRCALPHA)
    v.fill((0, 0, 8, 110))
    surf.blit(v, (0, 0))
    rng = random.Random(4)
    for i in range(46):
        x = (rng.random() * 480 + math.sin(t * 0.4 + i) * 12) % 480
        y = (rng.random() * 270 - t * (6 + i % 7)) % 270
        c = (170, 140, 255) if i % 2 else (220, 200, 255)
        surf.set_at((int(x), int(y)), c)


def marque(surf, cx, cy, t, taille=24):
    """La Marque de l'Outsider : losange vivant, œil central."""
    p = 1 + math.sin(t * 2) * 0.08
    r = int(taille * p)
    for k, c in enumerate(((60, 30, 110), (140, 80, 230), (230, 200, 255))):
        rr = r - k * 4
        pygame.draw.polygon(surf, c, [(cx, cy - rr), (cx + rr * 0.7, cy), (cx, cy + rr), (cx - rr * 0.7, cy)], 2 if k < 2 else 0)
    pygame.draw.circle(surf, (20, 10, 40), (cx, cy), max(2, r // 5))


# ----------------------------------------------------------------------------------------
class SceneTitre:
    transparente = False

    def __init__(self, jeu):
        self.t = 0.0
        items = ["Nouvelle partie", "Continuer", "Options", "Quitter"]
        self.menu = hud.Menu(items, largeur=120, visibles=4, taille=18, desactives=set() if existe() else {1}, hauteur_ligne=17)
        jeu.audio.musique("titre")

    def handle(self, event, jeu):
        a = jeu.clavier.action(event)
        i = self.menu.traiter(a, jeu.souris, event)
        if a in ("haut", "bas"):
            jeu.audio.jouer("curseur")
        if i is None:
            return
        jeu.audio.jouer("valide")
        if i == 0:
            jeu.pousser(SceneChoixEquipe(jeu))
        elif i == 1:
            e = charger()
            if e:
                from exploration.exploration import SceneExploration
                jeu.etat = e
                jeu.reinitialiser(SceneExploration(jeu, e.zone, "pos"))
        elif i == 2:
            from parametre.options import SceneOptions
            jeu.pousser(SceneOptions(jeu))
        else:
            jeu.quitter = True

    def skyline(self, surf):
        """Trois plans de silhouettes de la ville baleinière défilant lentement."""
        if not hasattr(self, "_sky"):
            rng = random.Random(9)
            self._sky = []
            for plan, (col, haut) in enumerate((((26, 18, 52), 70), ((16, 10, 34), 100), ((8, 5, 20), 130))):
                larg = 720
                img = pygame.Surface((larg, 130), pygame.SRCALPHA)
                x = 0
                while x < larg:
                    w, h = rng.randint(18, 42), rng.randint(30, haut)
                    pygame.draw.rect(img, col, (x, 130 - h, w, h))
                    pygame.draw.polygon(img, col, [(x - 2, 130 - h), (x + w // 2, 130 - h - rng.randint(8, 22)), (x + w + 2, 130 - h)])
                    if rng.random() < 0.4:
                        pygame.draw.rect(img, col, (x + w - 8, 130 - h - 34, 4, 34))
                    for wy in range(130 - h + 8, 122, 12):
                        if rng.random() < 0.35 and plan > 0:
                            pygame.draw.rect(img, (255, 190, 100), (x + 4 + rng.choice([0, w // 2]), wy, 3, 5))
                    x += w + rng.randint(0, 4)
                self._sky.append(img)
        for plan, img in enumerate(self._sky):
            dec = int(self.t * (3 + plan * 4)) % 720
            for ox in (-dec, 720 - dec):
                surf.blit(img, (ox, 140 + plan * 4))
        v = pygame.Surface((480, 270), pygame.SRCALPHA)
        v.fill((6, 4, 16, 0))
        surf.blit(px.vignette(160), (0, 0))

    def update(self, dt, jeu):
        self.t += dt

    def reprendre(self, jeu):
        jeu.audio.musique("titre")
        self.menu.desactives = set() if existe() else {1}

    def draw(self, surf, jeu):
        fond_brume(surf, self.t)
        self.skyline(surf)
        surf.blit(px.lumiere(90, (50, 30, 110)), (240 - 90, 70 - 90), special_flags=pygame.BLEND_RGB_ADD)
        marque(surf, 240, 70, self.t, 30)
        hud.texte_degrade(surf, "HONORED FANTASY", (240, 92), 48, (255, 236, 170), (200, 130, 60))
        hud.texte(surf, "Les condamnés de Pendysia", (240, 134), (205, 195, 235), 18, centre=True)
        for i, (n, e) in enumerate(zip(bot_equipe.DEFAUT, bot_equipe.ESPECES_SLOTS)):
            surf.blit(px.chibi(n, "bas", 0, 2, espece=e), (150 + i * 52, 214 + int(math.sin(self.t * 2 + i) * 2)))
        self.menu.dessiner(surf, (180, 166), cadre=True)
        hud.texte(surf, "ZQSD / flèches : déplacer   Entrée : valider   Échap : retour   Tab : menu   P : pouvoirs", (240, 258), hud.GRIS, 13, centre=True)


# ----------------------------------------------------------------------------------------
class SceneChoixEquipe:
    """Composition libre du groupe : pour chacun des 4 emplacements, un nom au choix et une classe quelconque (doublons permis)."""
    transparente = False

    def __init__(self, jeu):
        self.ids = list(registre.JOUABLES)
        self.classes = list(bot_equipe.DEFAUT)
        self.noms = list(bot_equipe.NOMS_SLOTS)
        self.noms_modifies = [False] * 4
        self.i = 0
        self.edition = False
        self.t = 0.0

    def changer_classe(self, k, sens):
        ancien = self.classes[k]
        self.classes[k] = self.ids[(self.ids.index(ancien) + sens) % len(self.ids)]

    def handle(self, event, jeu):
        if self.edition:                       # saisie du nom : on lit les touches brutes (z, q, s, d... sont des lettres)
            if event.type != pygame.KEYDOWN:
                return
            k = self.i
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE):
                self.edition = False
                if not self.noms[k].strip():
                    self.noms[k] = bot_equipe.NOMS_SLOTS[k]
                    self.noms_modifies[k] = False
                jeu.audio.jouer("valide")
            elif event.key == pygame.K_BACKSPACE:
                self.noms[k] = self.noms[k][:-1]
            elif event.unicode and event.unicode.isprintable() and len(self.noms[k]) < bot_equipe.LONGUEUR_NOM_MAX:
                self.noms[k] += event.unicode
                jeu.audio.jouer("curseur")
            return
        a = jeu.clavier.action(event)
        if a == "haut":
            self.i = (self.i - 1) % 5; jeu.audio.jouer("curseur")
        elif a == "bas":
            self.i = (self.i + 1) % 5; jeu.audio.jouer("curseur")
        elif a in ("gauche", "droite") and self.i < 4:
            self.changer_classe(self.i, -1 if a == "gauche" else 1); jeu.audio.jouer("curseur")
        elif a == "annuler":
            jeu.retour()
        elif a == "valider":
            if self.i < 4:
                self.edition = True
                if not self.noms_modifies[self.i]:
                    self.noms[self.i] = ""
                self.noms_modifies[self.i] = True
                jeu.audio.jouer("valide")
            else:
                jeu.audio.jouer("niveau")
                jeu.etat = EtatJeu(bot_equipe.creer_equipe(list(zip(self.noms, self.classes))))
                jeu.reinitialiser(SceneIntro(jeu))

    def update(self, dt, jeu):
        self.t += dt

    def draw(self, surf, jeu):
        fond_brume(surf, self.t)
        hud.texte(surf, "COMPOSEZ VOTRE GROUPE", (14, 8), hud.OR, 22)
        sel_start = self.i == 4
        hud.fenetre(surf, (320, 6, 148, 22), bordure=hud.OR if sel_start else hud.LAITON)
        hud.texte(surf, "Commencer", (394, 11), hud.OR if sel_start else hud.BLANC, 17, centre=True)
        for k in range(4):
            cid = self.classes[k]
            cl = registre.obtenir(cid)
            y = 32 + k * 48
            sel = self.i == k
            hud.fenetre(surf, (12, y, 456, 46), bordure=hud.OR if sel else hud.LAITON)
            surf.blit(px.chibi(cid, "bas", 0, 2, True, espece=bot_equipe.ESPECES_SLOTS[k]), (18, y - 5 + int(math.sin(self.t * 4) * 2 * sel)))
            hud.texte(surf, f"#{k + 1}", (62, y + 4), hud.GRIS, 13)
            hud.texte(surf, px.ESPECES[bot_equipe.ESPECES_SLOTS[k]]["nom"], (240, y + 29), hud.OR, 12, droite=True)
            nom = self.noms[k]
            editing = sel and self.edition
            champ = pygame.Rect(80, y + 4, 150, 20)
            pygame.draw.rect(surf, (8, 12, 30), champ)
            pygame.draw.rect(surf, hud.OR if editing else (90, 90, 120), champ, 1)
            caret = "_" if editing and int(self.t * 2) % 2 == 0 else ""
            hud.texte(surf, nom + caret, (champ.x + 5, champ.y + 3), hud.BLANC, 17)
            hud.texte(surf, "Entrée : renommer" if sel and not self.edition else ("Entrée : valider" if editing else ""), (80, y + 29), hud.GRIS, 12)
            hud.texte(surf, "<", (252, y + 6), hud.OR if sel else hud.GRIS, 20)
            hud.texte(surf, cl.nom, (350, y + 8), hud.BLANC, 18, centre=True)
            hud.texte(surf, ">", (448, y + 6), hud.OR if sel else hud.GRIS, 20, droite=True)
            hud.texte(surf, cl.role.split(" / ")[0], (350, y + 27), hud.GRIS, 13, centre=True)
        # fiche de la classe survolée
        hud.fenetre(surf, (12, 226, 456, 40))
        if self.i < 4:
            cl = registre.obtenir(self.classes[self.i])
            s = cl.stats_base
            hud.texte(surf, "  ".join(f"{n} {s[n]}" for n in ("PV", "Mana", "FOR", "RES", "INT", "DEX", "AGI")), (20, 230), hud.BLANC, 14)
            kit = ", ".join(act.ARMES_NOMS[e] for e in cl.equipement) + ((", " + ", ".join(act.SORTS[x].nom for x in cl.sorts(1))) if cl.sorts(1) else "")
            hud.texte(surf, f"Kit : {kit}   |   {cl.passif}", (20, 247), hud.VIOLET, 12)
        else:
            res = {}
            for c in self.classes:
                res[registre.obtenir(c).nom] = res.get(registre.obtenir(c).nom, 0) + 1
            hud.texte(surf, "Groupe : " + ", ".join(f"{n} x{k}" if k > 1 else n for n, k in res.items()), (20, 230), hud.BLANC, 15)
            hud.texte(surf, "Haut/Bas : emplacement   Gauche/Droite : classe   Entrée : renommer / commencer", (20, 247), hud.GRIS, 12)


# ----------------------------------------------------------------------------------------
class SceneTexte:
    """Défilement de texte (intro / fin)."""
    transparente = False

    def __init__(self, jeu, pages, suite, titre=None, musique="titre"):
        self.pages, self.suite, self.p, self.t, self.titre = pages, suite, 0, 0.0, titre
        jeu.audio.musique(musique)

    def handle(self, event, jeu):
        a = jeu.clavier.action(event)
        if a in ("valider", "annuler") or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
            if self.t < len(self.pages[self.p]):
                self.t = len(self.pages[self.p])
                return
            self.p += 1
            self.t = 0
            if self.p >= len(self.pages):
                self.suite(jeu)

    def update(self, dt, jeu):
        self.t += dt * 40

    def draw(self, surf, jeu):
        fond_brume(surf, self.t / 40)
        marque(surf, 240, 52, self.t / 40, 18)
        if self.p < len(self.pages):
            hud.texte_multiligne(surf, self.pages[self.p][:int(self.t)], pygame.Rect(40, 100, 400, 140), hud.BLANC, 18, 6)
            hud.texte(surf, f"{self.p + 1}/{len(self.pages)}", (470, 256), hud.GRIS, 13, droite=True)


def SceneIntro(jeu):
    def go(j):
        from exploration.exploration import SceneExploration
        j.reinitialiser(SceneExploration(j, 0, "prev"))
    return SceneTexte(jeu, TEXTE_INTRO, go)


class SceneFin(SceneTexte):
    def __init__(self, jeu):
        def fin(j):
            j.reinitialiser(SceneCredits(j))
        super().__init__(jeu, TEXTE_FIN, fin, musique="titre")


class SceneCredits:
    transparente = False

    def __init__(self, jeu):
        self.t = 0.0

    def handle(self, event, jeu):
        if jeu.clavier.action(event) == "valider" and self.t > 1.5:
            jeu.reinitialiser(SceneTitre(jeu))

    def update(self, dt, jeu):
        self.t += dt

    def draw(self, surf, jeu):
        fond_brume(surf, self.t)
        marque(surf, 240, 60, self.t, 26)
        hud.titre(surf, "FIN", 90, hud.OR, 50)
        hud.texte(surf, "Pendysia est sauvée. Pour l'instant.", (240, 150), hud.BLANC, 18, centre=True)
        if int(self.t * 2) % 2 == 0:
            hud.texte(surf, "Entrée : retour au titre", (240, 240), hud.GRIS, 14, centre=True)


class SceneGameOver:
    transparente = False

    def __init__(self, jeu):
        self.t = 0.0
        self.menu = hud.Menu(["Charger la dernière sauvegarde", "Retour au titre"], largeur=210, visibles=2, taille=17, desactives=set() if existe() else {0}, hauteur_ligne=17)
        jeu.audio.musique(None)

    def handle(self, event, jeu):
        i = self.menu.traiter(jeu.clavier.action(event), jeu.souris, event)
        if i == 0:
            from exploration.exploration import SceneExploration
            e = charger()
            if e:
                jeu.etat = e
                jeu.reinitialiser(SceneExploration(jeu, e.zone, "pos"))
        elif i == 1:
            jeu.reinitialiser(SceneTitre(jeu))

    def update(self, dt, jeu):
        self.t += dt

    def draw(self, surf, jeu):
        surf.fill((6, 4, 10))
        marque(surf, 240, 80, self.t * 0.5, 20)
        hud.texte(surf, "Les condamnés sont tombés.", (240, 110), (210, 60, 70), 28, centre=True)
        hud.texte(surf, "L'Outsider détourne le regard.", (240, 138), hud.GRIS, 16, centre=True)
        self.menu.dessiner(surf, (135, 175))


# ----------------------------------------------------------------------------------------
class SceneMenuPause:
    transparente = False

    def __init__(self, jeu, exploration):
        self.jeu, self.expl = jeu, exploration
        self.vue = "main"
        self.main = hud.Menu(["Équipe", "Objets", "Équipement", "Sauvegarder", "Options", "Titre"], largeur=84, visibles=6, taille=16, hauteur_ligne=16)
        self.sous = None
        self.hero = 0
        self.slot = "arme"
        self.t = 0.0
        self.obj = None

    # -- helpers
    def etat(self):
        return self.jeu.etat

    def heros_menu(self):
        return hud.Menu([f"{p.nom}  N{p.niveau}" for p in self.etat().equipe], largeur=120, visibles=4, taille=16, hauteur_ligne=16)

    def handle(self, event, jeu):
        a = jeu.clavier.action(event)
        et = self.etat()
        if self.vue == "main":
            if a in ("annuler", "menu"):
                jeu.retour(); return
            i = self.main.traiter(a, jeu.souris, event)
            if a in ("haut", "bas"):
                jeu.audio.jouer("curseur")
            if i is None:
                return
            jeu.audio.jouer("valide")
            if i == 0:
                self.vue, self.sous = "equipe", self.heros_menu()
            elif i == 1:
                self.ouvrir_objets()
            elif i == 2:
                self.vue, self.sous = "equip_hero", self.heros_menu()
            elif i == 3:
                et.pos = (self.expl.x, self.expl.y)
                ok = sauvegarder(et)
                jeu.notif.ajouter("Partie sauvegardée." if ok else "Échec de la sauvegarde.", hud.VERT if ok else hud.ROUGE)
            elif i == 4:
                from parametre.options import SceneOptions
                jeu.pousser(SceneOptions(jeu))
            else:
                jeu.reinitialiser(SceneTitre(jeu))
            return
        if a == "annuler":
            jeu.audio.jouer("annule")
            self.page_pouvoirs = False
            retour = {"equipe": "main", "objets": "main", "objets_cible": "objets", "equip_hero": "main", "equip_slot": "equip_hero", "equip_choix": "equip_slot"}[self.vue]
            self.vue = retour
            if retour == "objets":
                self.ouvrir_objets(garder=True)
            elif retour == "equip_hero":
                self.sous = self.heros_menu()
            elif retour == "equip_slot":
                self.ouvrir_slot()
            return
        i = self.sous.traiter(a, jeu.souris, event) if self.sous else None
        if a in ("haut", "bas"):
            jeu.audio.jouer("curseur")
        if i is None:
            return
        jeu.audio.jouer("valide")
        v = self.vue
        if v == "equipe":
            self.hero = i
            self.page_pouvoirs = not getattr(self, "page_pouvoirs", False)
        elif v == "objets":
            self.obj = self.ids[i]
            if self.obj.type == "conso" and ("pv_pct" in self.obj.effet or "mana_pct" in self.obj.effet or "revive" in self.obj.effet):
                self.vue, self.sous = "objets_cible", self.heros_menu()
            else:
                jeu.notif.ajouter("Cet objet ne s'utilise qu'en combat ou s'équipe.", hud.GRIS)
        elif v == "objets_cible":
            self.utiliser(et.equipe[i])
        elif v == "equip_hero":
            self.hero = i
            self.ouvrir_slot()
        elif v == "equip_slot":
            self.slot = ("arme", "talisman")[i]
            self.ouvrir_choix()
        elif v == "equip_choix":
            self.equiper(i)

    def ouvrir_objets(self, garder=False):
        gr = groupes(self.etat().sac.objets)
        self.ids = [o for o, n in gr]
        self.vue = "objets"
        cur = self.sous.curseur if (garder and self.sous) else 0
        self.sous = hud.Menu([f"{o.nom} x{n}" for o, n in gr] or ["(vide)"], largeur=160, visibles=11, taille=15, hauteur_ligne=14)
        self.sous.curseur = min(cur, max(0, len(self.ids) - 1))
        if not self.ids:
            self.sous.desactives = {0}

    def utiliser(self, p):
        o = self.obj
        ok = False
        if "revive" in o.effet and not p.vivant:
            p.pv = max(1, int(p.pv_max * o.effet["revive"])); ok = True
        if "pv_pct" in o.effet and p.vivant and p.pv < p.pv_max:
            p.pv = min(p.pv_max, p.pv + int(p.pv_max * o.effet["pv_pct"] * p.classe.efficacite_potion)); ok = True
        if "mana_pct" in o.effet and p.mana < p.mana_max:
            p.mana = min(p.mana_max, p.mana + int(p.mana_max * o.effet["mana_pct"])); ok = True
        if ok:
            self.etat().sac.retirer(o)
            self.jeu.audio.jouer("soin")
        else:
            self.jeu.audio.jouer("erreur")
        self.ouvrir_objets(garder=True)

    def ouvrir_slot(self):
        p = self.etat().equipe[self.hero]
        self.vue = "equip_slot"
        self.sous = hud.Menu([f"Arme : {p.nom_arme}", f"Talisman : {p.talisman.nom if p.talisman else '(aucun)'}"], largeur=250, visibles=2, taille=15, hauteur_ligne=16)

    def ouvrir_choix(self):
        p = self.etat().equipe[self.hero]
        if self.slot == "arme":
            self.cands = [o for o in self.etat().sac.objets if o.type == "arme" and o.classe == p.classe_id]
        else:
            self.cands = [o for o in self.etat().sac.objets if o.type == "talisman"]
        labels = ["(retirer)"] + [f"{o.nom}  [{o.desc}]" for o in self.cands]
        self.vue = "equip_choix"
        self.sous = hud.Menu(labels, largeur=290, visibles=11, taille=14, hauteur_ligne=14)

    def equiper(self, i):
        p = self.etat().equipe[self.hero]
        sac = self.etat().sac
        courant = p.arme if self.slot == "arme" else p.talisman
        nouveau = self.cands[i - 1] if i > 0 else None
        ratio = (p.pv / max(1, p.pv_max), p.mana / max(1, p.mana_max))
        if courant is not None and (self.slot == "talisman" or courant is not None):
            sac.ajouter(courant)
        if nouveau is not None:
            sac.retirer(nouveau)
        if self.slot == "arme":
            p.arme = nouveau
        else:
            p.talisman = nouveau
        p.pv = min(p.pv_max, max(1 if p.pv > 0 else 0, int(p.pv_max * ratio[0]))) if p.pv > 0 else 0
        p.mana = min(p.mana_max, int(p.mana_max * ratio[1]))
        self.jeu.audio.jouer("objet")
        self.ouvrir_slot()

    def update(self, dt, jeu):
        self.t += dt

    def draw(self, surf, jeu):
        surf.fill((10, 12, 24))
        fond = px.fond_combat("ville", "void")
        surf.blit(fond, (0, 0)); v = pygame.Surface((480, 270), pygame.SRCALPHA); v.fill((6, 8, 22, 200)); surf.blit(v, (0, 0))
        et = self.etat()
        hud.fenetre(surf, (6, 6, 96, 118))
        self.main.dessiner(surf, (14, 12), actif=self.vue == "main", cadre=False)
        hud.fenetre(surf, (6, 130, 96, 60))
        hud.texte(surf, f"Or  {et.or_}", (14, 136), hud.OR, 15)
        hud.texte(surf, f"Runes {len(et.runes)}/6", (14, 150), hud.VIOLET, 15)
        h = int(et.temps // 3600); m = int(et.temps % 3600 // 60)
        hud.texte(surf, f"Temps {h}:{m:02d}", (14, 164), hud.BLANC, 15)
        hud.texte(surf, f"Pas {et.pas_total}", (14, 176), hud.GRIS, 14)
        hud.fenetre(surf, (108, 6, 366, 258))
        v = self.vue
        if v == "main":
            self.dessiner_apercu(surf)
        elif v == "equipe":
            self.sous.dessiner(surf, (120, 16), cadre=False)
            if getattr(self, "page_pouvoirs", False):
                self.dessiner_pouvoirs(surf, et.equipe[self.sous.curseur], (250, 14))
            else:
                self.dessiner_fiche(surf, et.equipe[self.sous.curseur], (250, 14))
        elif v in ("objets", "objets_cible"):
            self.dessiner_objets(surf)
        else:
            self.dessiner_equipement(surf)

    def dessiner_apercu(self, surf):
        for i, p in enumerate(self.etat().equipe):
            y = 16 + i * 60
            surf.blit(px.chibi(p.classe.sprite, "bas", 0, 2, espece=p.espece), (118, y + 2))
            hud.texte(surf, f"{p.nom}  -  {p.classe.nom}  N{p.niveau}", (160, y), hud.OR, 16)
            hud.barre(surf, (160, y + 18, 150, 6), p.pv / max(1, p.pv_max), hud.couleur_pv(p.pv / max(1, p.pv_max)))
            hud.texte(surf, f"PV {p.pv}/{p.pv_max}", (318, y + 15), hud.BLANC, 14)
            hud.barre(surf, (160, y + 30, 150, 4), p.mana / max(1, p.mana_max), (90, 140, 255))
            hud.texte(surf, f"MP {p.mana}/{p.mana_max}", (318, y + 27), hud.BLANC, 14)
            hud.barre(surf, (160, y + 40, 150, 3), p.xp / max(1, p.xp_suivant()), (200, 160, 60))
            hud.texte(surf, f"XP {p.xp}/{p.xp_suivant()}", (318, y + 38), hud.GRIS, 13)

    def dessiner_fiche(self, surf, p, pos):
        x, y = pos
        surf.blit(px.chibi(p.classe.sprite, "bas", 0, 3, True, espece=p.espece), (x + 150, y))
        hud.texte(surf, f"{p.nom} - {p.classe.nom} (niv {p.niveau})", (x, y), hud.OR, 17)
        hud.texte(surf, p.classe.role, (x, y + 16), hud.GRIS, 13)
        s = p.stats()
        base = p.classe.stats(p.niveau)
        for k, nom in enumerate(("PV", "Mana", "FOR", "RES", "INT", "DEX", "AGI")):
            bonus = s[nom] - base[nom]
            hud.texte(surf, f"{nom:4s} {s[nom]}" + (f" (+{bonus})" if bonus else ""), (x, y + 36 + k * 14), hud.VERT if bonus else hud.BLANC, 15)
        hud.texte(surf, f"Arme : {p.nom_arme} ({p.arme_base})", (x, y + 138), hud.BLANC, 14)
        hud.texte(surf, f"Talisman : {p.talisman.nom if p.talisman else '-'}", (x, y + 152), hud.BLANC, 14)
        hud.texte_multiligne(surf, p.classe.passif, pygame.Rect(x, y + 168, 215, 30), hud.VIOLET, 13)
        hud.texte(surf, f"Pouvoirs : {len(p.sorts())}   Passifs : {len(p.classe.passifs(p.niveau))}   (Entrée : détail)", (x, y + 200), hud.BLANC, 13)
        hud.texte(surf, f"Armes : {', '.join(act.ARMES_NOMS[e] for e in p.classe.equipement)}", (x, y + 214), hud.GRIS, 13)

    def dessiner_pouvoirs(self, surf, p, pos):
        """Page détaillée : passifs de l'Outsider, pouvoirs connus avec leur coût, prochain déblocage."""
        from classe import PASSIFS
        from classe.formules import cout_mana
        x, y = pos
        hud.texte(surf, f"{p.nom} - pouvoirs de l'Outsider", (x, y), hud.OR, 16)
        yy = y + 18
        intel = p.stats()["INT"]
        for pid in p.classe.passifs(p.niveau):
            hud.texte(surf, "* " + PASSIFS[pid][0], (x, yy), hud.VERT, 13); yy += 11
        if p.classe.passifs(p.niveau):
            yy += 3
        for sp in p.sorts():
            sort = act.SORTS[sp]
            if yy > 236:
                hud.texte(surf, "...", (x, yy), hud.GRIS, 13); break
            hud.texte(surf, f"{sort.nom}", (x, yy), hud.BLANC, 13)
            hud.texte(surf, f"{cout_mana(sort.cout, intel, p.classe.reduction_mana)} MP", (x + 205, yy), hud.BLEU, 13, droite=True)
            yy += 11
        if not p.sorts():
            hud.texte(surf, "Aucun pouvoir : seuls la Sorcière et le Harponneur", (x, yy), hud.GRIS, 13)
            hud.texte(surf, "reçoivent les dons de l'Outsider.", (x, yy + 11), hud.GRIS, 13)
        suivants = [(lv, ("sort", s_)) for lv, s_ in p.classe.sorts_par_niveau.items() if lv > p.niveau] + \
                   [(lv, ("passif", s_)) for lv, s_ in p.classe.passifs_par_niveau.items() if lv > p.niveau]
        if suivants:
            lv, (genre, ident) = min(suivants, key=lambda t: t[0])
            nom = act.SORTS[ident].nom if genre == "sort" else PASSIFS[ident][0]
            hud.texte(surf, f"Prochain : {nom} (niv {lv})", (x, 246), hud.VIOLET, 13)

    def dessiner_objets(self, surf):
        self.sous.dessiner(surf, (120, 16), cadre=False)
        if self.vue == "objets_cible":
            hud.texte(surf, "Utiliser sur :", (320, 16), hud.OR, 16)
            sub = self.heros_menu()
            sub.curseur = self.sous.curseur
            self.sous.dessiner(surf, (320, 32), cadre=False)
            for i, p in enumerate(self.etat().equipe):
                hud.texte(surf, f"PV {p.pv}/{p.pv_max}  MP {p.mana}/{p.mana_max}", (330, 100 + i * 14), hud.BLANC, 13)
        if self.vue == "objets" and self.ids:
            o = self.ids[self.sous.curseur]
            surf.blit(o.icone, (320, 18))
            hud.texte(surf, o.nom, (338, 18), px.RARETE_COULEURS[o.rarete], 16)
            hud.texte(surf, px.RARETE_NOMS[o.rarete], (338, 32), hud.GRIS, 13)
            hud.texte_multiligne(surf, o.desc, pygame.Rect(320, 52, 146, 60), hud.BLANC, 14)
            hud.texte(surf, f"Valeur : {o.valeur}", (320, 118), hud.OR, 14)

    def dessiner_equipement(self, surf):
        v = self.vue
        if v == "equip_hero":
            self.sous.dessiner(surf, (120, 16), cadre=False)
            self.dessiner_fiche(surf, self.etat().equipe[self.sous.curseur], (250, 14))
            return
        p = self.etat().equipe[self.hero]
        hud.texte(surf, f"{p.nom} - {p.classe.nom}", (120, 14), hud.OR, 17)
        self.sous.dessiner(surf, (120, 36), cadre=False)
        if v == "equip_choix":
            i = self.sous.curseur
            if i > 0:
                o = self.cands[i - 1]
                surf.blit(o.icone, (120, 214))
                hud.texte(surf, f"{o.nom} - {px.RARETE_NOMS[o.rarete]}", (138, 214), px.RARETE_COULEURS[o.rarete], 15)
                hud.texte(surf, o.desc, (138, 230), hud.BLANC, 14)


# ----------------------------------------------------------------------------------------
class SceneBoutique:
    transparente = False

    def __init__(self, jeu, magasin):
        self.jeu, self.m = jeu, magasin
        self.mode = "choix"
        self.main = hud.Menu(["Acheter", "Vendre", "Quitter"], largeur=70, visibles=3, taille=16, hauteur_ligne=16)
        self.liste = None
        self.t = 0.0

    def ouvrir(self, mode):
        self.mode = mode
        if mode == "acheter":
            self.items = self.m.stock
            labels = [f"{o.nom}   {o.prix}" for o in self.items]
        else:
            self.items = [o for o in self.jeu.etat.sac.objets if o.type != "rune"]
            gr = []
            vus = {}
            for o in self.items:
                if o.id in vus:
                    continue
                vus[o.id] = 1
                gr.append(o)
            self.items = gr
            labels = [f"{o.nom} x{sum(1 for z in self.jeu.etat.sac.objets if z.id == o.id)}   {prix_revente(o)}" for o in self.items]
        self.liste = hud.Menu(labels or ["(rien)"], largeur=210, visibles=12, taille=14, hauteur_ligne=15)
        if not self.items:
            self.liste.desactives = {0}

    def handle(self, event, jeu):
        a = jeu.clavier.action(event)
        et = jeu.etat
        if self.mode == "choix":
            if a == "annuler":
                jeu.retour(); return
            i = self.main.traiter(a, jeu.souris, event)
            if i is not None:
                jeu.audio.jouer("valide")
                if i == 2:
                    jeu.retour()
                else:
                    self.ouvrir(("acheter", "vendre")[i])
            return
        if a == "annuler":
            jeu.audio.jouer("annule"); self.mode = "choix"; return
        i = self.liste.traiter(a, jeu.souris, event)
        if a in ("haut", "bas"):
            jeu.audio.jouer("curseur")
        if i is None or not self.items:
            return
        o = self.items[i]
        if self.mode == "acheter":
            if self.m.acheter(et, o):
                jeu.audio.jouer("objet"); jeu.notif.ajouter(f"Acheté : {o.nom}", hud.VERT, 1.5)
            else:
                jeu.audio.jouer("erreur"); jeu.notif.ajouter("Pas assez d'or.", hud.ROUGE, 1.5)
        else:
            cur = self.liste.curseur
            g = next((x for x in et.sac.objets if x.id == o.id), None)
            gain = self.m.vendre(et, g) if g else 0
            if gain:
                jeu.audio.jouer("objet"); jeu.notif.ajouter(f"Vendu : {o.nom} (+{gain})", hud.OR, 1.5)
            self.ouvrir("vendre")
            self.liste.curseur = min(cur, max(0, len(self.items) - 1))

    def update(self, dt, jeu):
        self.t += dt

    def draw(self, surf, jeu):
        fond_brume(surf, self.t, "realme" if self.m.zone.monde == "realme" else "void")
        hud.fenetre(surf, (6, 6, 468, 258))
        hud.texte(surf, f"Boutique - {self.m.zone.nom}", (16, 12), hud.OR, 18)
        hud.texte(surf, f"Prospérité {self.m.prosperite}/4   prix x{self.m.multiplicateur:.2f}   Revente 80 %", (16, 28), hud.GRIS, 13)
        hud.texte(surf, f"Or : {jeu.etat.or_}", (464, 12), hud.OR, 18, droite=True)
        self.main.dessiner(surf, (18, 50), actif=self.mode == "choix", cadre=True)
        if self.liste and self.mode != "choix":
            self.liste.dessiner(surf, (110, 48), cadre=False)
            if self.items:
                o = self.items[self.liste.curseur]
                surf.blit(o.icone, (340, 52))
                hud.texte(surf, o.nom, (358, 52), px.RARETE_COULEURS[o.rarete], 16)
                hud.texte(surf, px.RARETE_NOMS[o.rarete], (358, 66), hud.GRIS, 13)
                hud.texte_multiligne(surf, o.desc, pygame.Rect(340, 88, 126, 60), hud.BLANC, 14)
                if o.type == "arme":
                    hud.texte(surf, f"Pour : {registre.obtenir(o.classe).nom}", (340, 130), hud.VERT, 14)
                prix = o.prix if self.mode == "acheter" else prix_revente(o)
                hud.texte(surf, ("Prix : " if self.mode == "acheter" else "Rachat : ") + str(prix), (340, 146), hud.OR, 15)


class SceneMenuPouvoirs:
    """Menu des pouvoirs de l'Outsider utilisables en exploration (touche P)."""
    transparente = False

    def __init__(self, jeu, exploration):
        from exploration import pouvoirs
        self.jeu, self.expl, self.mod = jeu, exploration, pouvoirs
        self.liste = pouvoirs.disponibles(jeu.etat)
        labels = [f"{info['nom']}  ({info['cout']} MP, {p.nom})" for pid, info, p in self.liste] or ["(aucun pouvoir connu)"]
        self.menu = hud.Menu(labels, largeur=250, visibles=7, taille=15, hauteur_ligne=16, desactives=set() if self.liste else {0})

    def handle(self, event, jeu):
        a = jeu.clavier.action(event)
        if a in ("annuler", "pouvoir", "menu"):
            jeu.retour(); return
        i = self.menu.traiter(a, jeu.souris, event)
        if a in ("haut", "bas"):
            jeu.audio.jouer("curseur")
        if i is None or not self.liste:
            return
        pid, info, membre = self.liste[i]
        jeu.retour()                       # on revient à la carte avant d'agir (téléportation, vision...)
        ok, msg = self.mod.utiliser(self.expl, pid, membre)
        if not ok:
            jeu.audio.jouer("erreur")
            jeu.notif.ajouter(msg, hud.ROUGE, 2.2)

    def update(self, dt, jeu):
        self.expl.temps += dt * 0

    def draw(self, surf, jeu):
        self.expl.draw(surf, jeu)
        hud.fenetre(surf, (90, 50, 300, 150))
        hud.texte(surf, "Pouvoirs de l'Outsider", (240, 56), hud.OR, 18, centre=True)
        self.menu.dessiner(surf, (104, 82), cadre=False)
        if self.liste:
            pid, info, membre = self.liste[self.menu.curseur]
            hud.texte_multiligne(surf, info["desc"], pygame.Rect(104, 82 + 7 * 16 - 12, 272, 40), hud.GRIS, 13)
