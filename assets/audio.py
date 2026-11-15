"""Audio synthétisé (aucun fichier requis) : effets sonores et boucles musicales procédurales."""
import array
import math
import random
import pygame

TAUX = 22050


def _onde(freq, duree, forme="carre", vol=0.4, glisse=0.0, bruit=0.0, attaque=0.005):
    n = int(TAUX * duree)
    out = array.array("h")
    ph = 0.0
    rng = random.Random(3)
    for i in range(n):
        t = i / TAUX
        f = freq * (1 + glisse * (i / n))
        ph += f / TAUX
        if forme == "carre":
            v = 1.0 if (ph % 1) < 0.5 else -1.0
        elif forme == "scie":
            v = 2 * (ph % 1) - 1
        elif forme == "sin":
            v = math.sin(2 * math.pi * ph)
        else:
            v = rng.uniform(-1, 1)
        if bruit:
            v = v * (1 - bruit) + rng.uniform(-1, 1) * bruit
        env = min(1.0, t / attaque) * (1 - i / n) ** 1.5
        out.append(int(max(-1, min(1, v * env * vol)) * 32767))
    return out


def _concat(*sons):
    r = array.array("h")
    for s in sons:
        r.extend(s)
    return r


def _mixer(a, b):
    n = max(len(a), len(b))
    r = array.array("h", [0]) * n
    for i in range(len(a)):
        r[i] += a[i]
    for i in range(len(b)):
        r[i] = max(-32767, min(32767, r[i] + b[i]))
    return r


NOTES = {"do": 261.6, "re": 293.7, "mi": 329.6, "fa": 349.2, "sol": 392.0, "la": 440.0, "si": 493.9}


def _hz(n):
    return 440.0 * 2 ** ((n - 69) / 12)


class Audio:
    def __init__(self, conf):
        self.ok = False
        self.conf = conf["audio"]
        self.sons = {}
        self.musique_actuelle = None
        self.musiques = {}
        try:
            pygame.mixer.init(frequency=TAUX, size=-16, channels=1, buffer=512)
            self.ok = True
        except pygame.error:
            return
        self._creer_effets()
        self.regler(self.conf["volume"])

    def _s(self, data, vol=1.0):
        s = pygame.mixer.Sound(buffer=data.tobytes())
        s.set_volume(vol)
        return s

    def _creer_effets(self):
        self.sons["curseur"] = self._s(_onde(880, 0.03, "carre", 0.15))
        self.sons["valide"] = self._s(_concat(_onde(660, 0.04, "carre", 0.2), _onde(990, 0.07, "carre", 0.2)))
        self.sons["annule"] = self._s(_onde(330, 0.08, "carre", 0.2, -0.3))
        self.sons["erreur"] = self._s(_onde(150, 0.12, "carre", 0.25))
        self.sons["pas"] = self._s(_onde(90, 0.03, "bruit", 0.12))
        self.sons["coup"] = self._s(_mixer(_onde(160, 0.12, "bruit", 0.5, -0.5), _onde(220, 0.1, "carre", 0.3, -0.6)))
        self.sons["critique"] = self._s(_mixer(_onde(120, 0.25, "bruit", 0.6, -0.4), _concat(_onde(440, 0.06, "carre", 0.3), _onde(880, 0.14, "carre", 0.3, -0.5))))
        self.sons["rate"] = self._s(_onde(500, 0.14, "sin", 0.2, -0.6))
        self.sons["tir"] = self._s(_mixer(_onde(100, 0.18, "bruit", 0.8, -0.8), _onde(180, 0.1, "scie", 0.3, -0.9)))
        self.sons["explosion"] = self._s(_onde(70, 0.55, "bruit", 0.9, -0.6, 0.8))
        self.sons["magie"] = self._s(_concat(_onde(400, 0.08, "sin", 0.3, 1.5), _onde(800, 0.18, "sin", 0.3, 1.0)))
        self.sons["blink"] = self._s(_onde(300, 0.2, "scie", 0.3, 3.0))
        self.sons["temps"] = self._s(_concat(*[_onde(220 + 40 * (i % 2), 0.1, "sin", 0.3) for i in range(6)]))
        self.sons["soin"] = self._s(_concat(*[_onde(_hz(n), 0.08, "sin", 0.3) for n in (72, 76, 79, 84)]))
        self.sons["objet"] = self._s(_concat(_onde(1200, 0.05, "carre", 0.2), _onde(1600, 0.08, "carre", 0.2)))
        self.sons["rencontre"] = self._s(_concat(*[_onde(180 + 60 * (i % 3), 0.07, "scie", 0.35, 0.5) for i in range(8)]))
        self.sons["victoire"] = self._s(_concat(*[_onde(_hz(n), d, "carre", 0.25) for n, d in ((67, .1), (67, .1), (67, .1), (72, .3), (70, .12), (72, .4))]))
        self.sons["defaite"] = self._s(_concat(*[_onde(_hz(n), 0.3, "scie", 0.3) for n in (64, 62, 60, 55)]))
        self.sons["niveau"] = self._s(_concat(*[_onde(_hz(n), 0.07, "carre", 0.22) for n in (72, 76, 79, 84, 88)]))
        self.sons["ouvre"] = self._s(_concat(_onde(300, 0.05, "carre", 0.2), _onde(450, 0.05, "carre", 0.2), _onde(600, 0.1, "carre", 0.2)))
        self.sons["autel"] = self._s(_concat(*[_onde(_hz(n), 0.25, "sin", 0.25) for n in (60, 67, 72)]))

    def jouer(self, nom):
        if self.ok and not self.conf.get("muet") and nom in self.sons:
            self.sons[nom].play()

    def regler(self, vol):
        self.conf["volume"] = vol
        if self.ok:
            pygame.mixer.music.set_volume(vol) if False else None
            for s in self.sons.values():
                s.set_volume(max(0.0, min(1.0, vol * 1.6)))
            for m in self.musiques.values():
                m.set_volume(vol * 0.5)

    # -- musique : arpèges procéduraux en boucle ---------------------------------------
    def _fabriquer_musique(self, nom):
        presets = {
            "titre": (66, [0, 3, 7, 10, 7, 3], 0.42, "sin", [(0, 3, 7), (-2, 2, 5), (-4, 0, 3), (-2, 2, 5)]),
            "ville": (62, [0, 4, 7, 12, 7, 4], 0.30, "carre", [(0, 4, 7), (5, 9, 12), (7, 11, 14), (5, 9, 12)]),
            "foret": (60, [0, 7, 12, 7, 3, 7], 0.36, "sin", [(0, 3, 7), (-4, 0, 3), (-2, 2, 5), (-4, 0, 3)]),
            "donjon": (50, [0, 3, 6, 3, 0, -2], 0.5, "scie", [(0, 3, 6), (-1, 2, 5), (0, 3, 6), (-3, 0, 3)]),
            "void": (57, [0, 6, 11, 6, 1, 8], 0.44, "sin", [(0, 6, 10), (1, 5, 8), (-1, 4, 8), (1, 5, 8)]),
            "combat": (57, [0, 12, 7, 12, 3, 12, 7, 12], 0.16, "carre", [(0, 3, 7), (0, 3, 7), (-2, 1, 5), (-4, 0, 3)]),
            "boss": (50, [0, 12, 3, 12, 6, 12, 3, 12], 0.14, "scie", [(0, 3, 6), (-1, 2, 5), (-3, 0, 3), (-1, 2, 5)]),
        }
        base, arp, pas, forme, accords = presets[nom]
        data = array.array("h")
        for acc in accords:
            mesure = array.array("h")
            nb = int(len(arp) * 2)
            for k in range(nb):
                n = base + acc[0] + arp[k % len(arp)]
                mesure.extend(_onde(_hz(n), pas, forme, 0.13))
            basse = _onde(_hz(base + acc[0] - 24), pas * nb, "sin", 0.22)
            data.extend(_mixer(mesure, basse))
        return self._s(data, self.conf["volume"] * 0.5)

    def musique(self, nom):
        if not self.ok or nom == self.musique_actuelle:
            return
        if self.musique_actuelle in self.musiques:
            self.musiques[self.musique_actuelle].fadeout(400)
        self.musique_actuelle = nom
        if nom is None or self.conf.get("muet"):
            return
        if nom not in self.musiques:
            self.musiques[nom] = self._fabriquer_musique(nom)
        self.musiques[nom].set_volume(self.conf["volume"] * 0.5)
        self.musiques[nom].play(loops=-1, fade_ms=600)
