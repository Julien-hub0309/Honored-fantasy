"""Rencontres aléatoires : déclenchement selon le nombre de pas, et composition des escouades (bestiaire §4 / §5.1)."""
import random

from bot.bestiaire import creer_ennemi

# (poids, [(classe, effectif possible), ...])
COMPOSITIONS = {
    "ville": [(40, [("garde_urbain", (3,))]), (30, [("officier", (2,))]), (30, [("officier", (1,)), ("garde_urbain", (2,))])],
    "foret": [(50, [("monstre", (4, 5))]), (30, [("sorciere", (2,)), ("monstre", (2,))]), (20, [("sorciere", (3, 4))])],
    "donjon": "equiprobable",
}
SOLO = {"garde_urbain": (3,), "officier": (2,), "sorciere": (3, 4), "monstre": (4, 5), "moine": (2,), "harponneur": (2,)}
# probabilité de base par pas (après le seuil de pas minimal), x2 dans les hautes herbes
TAUX = {"ville": 0.030, "foret": 0.040, "donjon": 0.036}
PAS_MIN = 9


class RencontreAleatoire:
    def __init__(self, biome, niveau, void=False, rng=None):
        self.biome, self.niveau, self.void = biome, niveau, void
        self.rng = rng or random.Random()
        self.pas_depuis = 0

    def pas(self, herbe=False):
        """Appelé à chaque pas : retourne True si un combat se déclenche."""
        self.pas_depuis += 1
        if self.pas_depuis < PAS_MIN:
            return False
        p = TAUX[self.biome] * (2.0 if herbe else 1.0) * (1 + (self.pas_depuis - PAS_MIN) / 35)
        if self.rng.random() < p:
            self.pas_depuis = 0
            return True
        return False

    def composer(self):
        rng = self.rng
        comp = COMPOSITIONS[self.biome]
        if comp == "equiprobable":
            classe = rng.choice(list(SOLO))
            comp = [(1, [(classe, SOLO[classe])])]
            if classe == "officier" and rng.random() < 0.4:
                comp = [(1, [("officier", (1,)), ("garde_urbain", (2,))])]
        groupe = rng.choices([c[1] for c in comp], [c[0] for c in comp])[0]
        ennemis, compteur = [], {}
        for classe, eff in groupe:
            for _ in range(rng.choice(eff)):
                niv = max(1, self.niveau + rng.choice((-1, 0, 0, 1)))
                compteur[classe] = compteur.get(classe, 0) + 1
                ennemis.append(creer_ennemi(classe, niv, rng, self.void))
        for classe, n in compteur.items():           # suffixes A, B, C pour distinguer les homonymes
            if n > 1:
                k = 0
                for e in ennemis:
                    if e.classe.id == classe:
                        e.nom += " " + "ABCDE"[k]; k += 1
        return ennemis
