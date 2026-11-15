"""État global du jeu : Personnage persistant (PV/Mana/Rangs hors combat), EtatJeu et sauvegarde JSON.

Les PV/Mana sont recopiés vers/depuis le Combattant à chaque transition exploration <-> combat (cahier §8.3)."""
import json
import os
import time

import classe as registre
from classe.formules import xp_requis
from combat.combattant import Combattant
from exploration.objets import Inventaire, depuis_id

DOSSIER = os.path.join(os.path.expanduser("~"), ".honored_fantasy")
FICHIER = os.path.join(DOSSIER, "sauvegarde.json")
NIVEAU_MAX = 30


class Personnage:
    def __init__(self, nom, classe_id, niveau=1, slot=1):
        self.nom, self.classe_id, self.niveau, self.slot = nom, classe_id, niveau, slot
        self.classe = registre.obtenir(classe_id)
        self.xp = 0
        self.arme = None
        self.talisman = None
        self.espece = None
        self.pv = self.mana = 0
        self.pv = self.pv_max
        self.mana = self.mana_max

    # ----- statistiques (base de classe + talisman) -----
    def stats(self):
        s = self.classe.appliquer_passifs(self.classe.stats(self.niveau), self.niveau)
        if self.talisman:
            for k, v in self.talisman.bonus.items():
                s[k] = s.get(k, 0) + v
        return s

    @property
    def pv_max(self):
        return self.stats()["PV"]

    @property
    def mana_max(self):
        return self.stats()["Mana"]

    @property
    def arme_base(self):
        return self.arme.degats_base if self.arme else self.classe.arme["degats_base"]

    @property
    def nom_arme(self):
        return self.arme.nom if self.arme else self.classe.arme["nom"]

    @property
    def vivant(self):
        return self.pv > 0

    def sorts(self):
        return self.classe.sorts(self.niveau)

    def xp_suivant(self):
        return xp_requis(self.niveau)

    def gagner_xp(self, n):
        """Retourne la liste des niveaux gagnés (avec gains de stats) pour l'affichage."""
        rapports = []
        if self.niveau >= NIVEAU_MAX:
            return rapports
        self.xp += n
        while self.niveau < NIVEAU_MAX and self.xp >= self.xp_suivant():
            self.xp -= self.xp_suivant()
            avant = self.stats()
            sorts_avant = set(self.sorts())
            passifs_avant = set(self.classe.passifs(self.niveau))
            self.niveau += 1
            apres = self.stats()
            self.pv += apres["PV"] - avant["PV"]
            self.mana += apres["Mana"] - avant["Mana"]
            rapports.append(dict(niveau=self.niveau, gains={k: apres[k] - avant[k] for k in apres if apres[k] != avant[k]},
                                 sorts=[s for s in self.sorts() if s not in sorts_avant],
                                 passifs=[x for x in self.classe.passifs(self.niveau) if x not in passifs_avant]))
        return rapports

    def soigner_complet(self):
        self.pv, self.mana = self.pv_max, self.mana_max

    def en_combattant(self):
        s = self.stats()
        c = Combattant(self.nom, self.classe_id, self.niveau, s, True, arme_base=self.arme_base, perso=self, pv=max(0, self.pv), mana=self.mana)
        c.passifs = set(self.classe.passifs(self.niveau))
        c.espece = self.espece
        return c

    def vers_dict(self):
        return dict(nom=self.nom, espece=self.espece, classe=self.classe_id, niveau=self.niveau, slot=self.slot, xp=self.xp, pv=self.pv, mana=self.mana,
                    arme=[self.arme.id, self.arme.valeur] if self.arme else None,
                    talisman=[self.talisman.id, self.talisman.valeur] if self.talisman else None)

    @classmethod
    def depuis_dict(cls, d):
        p = cls(d["nom"], d["classe"], d["niveau"], d["slot"])
        p.espece = d.get("espece")
        p.xp, p.pv, p.mana = d["xp"], d["pv"], d["mana"]
        p.arme = depuis_id(*d["arme"]) if d["arme"] else None
        p.talisman = depuis_id(*d["talisman"]) if d["talisman"] else None
        return p


class EtatJeu:
    def __init__(self, equipe, graine=None):
        self.equipe = equipe
        self.sac = Inventaire()
        self.or_ = 120
        self.runes = []
        self.flags = {}
        self.coffres = set()
        self.boss_vaincus = set()
        self.zone = 0
        self.pos = None
        self.victoires = 0
        self.pas_total = 0
        self.graine = graine if graine is not None else int(time.time()) % 100000
        self.temps = 0.0
        self.autel_zone = (0, None)
        # kit de départ
        for _ in range(3):
            self.sac.ajouter(depuis_id("potion_vie"))
        for _ in range(2):
            self.sac.ajouter(depuis_id("potion_mana"))

    def vivants(self):
        return [p for p in self.equipe if p.vivant]

    def vers_dict(self):
        return dict(version=1, equipe=[p.vers_dict() for p in self.equipe], sac=self.sac.vers_dict(), or_=self.or_, runes=self.runes,
                    flags=self.flags, coffres=sorted(self.coffres), boss=sorted(self.boss_vaincus), zone=self.zone, pos=self.pos,
                    victoires=self.victoires, pas=self.pas_total, graine=self.graine, temps=self.temps, autel=list(self.autel_zone))

    @classmethod
    def depuis_dict(cls, d):
        e = cls([Personnage.depuis_dict(p) for p in d["equipe"]], d["graine"])
        e.sac = Inventaire.depuis_dict(d["sac"])
        e.or_, e.runes, e.flags = d["or_"], d["runes"], d["flags"]
        e.coffres, e.boss_vaincus = set(d["coffres"]), set(d["boss"])
        e.zone, e.pos, e.victoires, e.pas_total, e.temps = d["zone"], d["pos"], d["victoires"], d["pas"], d["temps"]
        e.autel_zone = tuple(d.get("autel", (0, None)))
        return e


def sauvegarder(etat):
    try:
        os.makedirs(DOSSIER, exist_ok=True)
        with open(FICHIER, "w", encoding="utf-8") as f:
            json.dump(etat.vers_dict(), f)
        return True
    except OSError:
        return False


def charger():
    try:
        with open(FICHIER, "r", encoding="utf-8") as f:
            return EtatJeu.depuis_dict(json.load(f))
    except (OSError, ValueError, KeyError):
        return None


def existe():
    return os.path.exists(FICHIER)
