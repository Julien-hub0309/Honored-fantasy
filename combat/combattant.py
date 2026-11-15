"""Un combattant (allié, ennemi ou boss) : données runtime du combat, synchronisées avec le Personnage."""
import classe as registre
from combat.pv import Pv
from combat.mana import Mana
from combat.rang import Rang

STATS = ("FOR", "RES", "INT", "DEX", "AGI")


class Combattant:
    def __init__(self, nom, classe_id, niveau, stats, allie, arme_base=None, sorts=None, perso=None,
                 boss=False, sprite=None, variante=0, void=False, pv=None, mana=None):
        self.nom = nom
        self.classe = registre.obtenir(classe_id)
        self.niveau = niveau
        self.allie = allie
        self.boss = boss
        self.perso = perso
        self.base = {k: stats[k] for k in STATS}
        self.pv = Pv(stats["PV"], pv)
        self.mana = Mana(stats["Mana"], mana)
        self.rang = Rang()
        self.arme_base = arme_base if arme_base is not None else self.classe.arme["degats_base"]
        self.sorts = list(sorts) if sorts is not None else self.classe.sorts(niveau)
        self.sprite = sprite or self.classe.sprite
        self.variante = variante
        self.void = void
        self.espece = None
        self.en_defense = False
        self.objet_utilise = False
        self.lien = None
        self.lien_duree = 0
        self.ia = None
        self.inventaire = []        # consommables (ennemis)
        self.xp = 0
        self.gain_or = 0
        self.butin = []
        self.cd = {}                # temps de recharge d'aptitudes (IA)
        self.phase = 0
        self.passifs = set()        # passifs de l'Outsider (agilite, soif_de_sang, vitalite, meurtrier_ombre)
        self.auto = False           # allié invoqué piloté par l'IA (assassin, sosie)
        self.tint = None            # teinte du sprite (invocations spectrales)
        # champs d'affichage (scène)
        self.pv_aff = float(self.pv.valeur)
        self.mana_aff = float(self.mana.valeur)
        self.alpha = 255
        self.offset = [0, 0]
        self.flash = 0.0

    @property
    def vivant(self):
        return self.pv.valeur > 0

    def a_passif(self, id_):
        """Passif propre ou partagé temporairement par Lien arcanique."""
        return id_ in self.passifs or self.rang.a("lien_" + id_)

    def stat(self, nom):
        v = self.rang.appliquer(nom, self.base[nom])
        if nom == "RES" and self.en_defense:
            v *= self.classe.mult_defense
        return v

    def cout_sort(self, sort):
        from classe.formules import cout_mana
        return cout_mana(sort.cout, self.stat("INT"), self.classe.reduction_mana)

    def synchroniser_vers_perso(self):
        """Écrit PV/Mana dans le personnage persistant (fin de combat)."""
        if self.perso is not None:
            self.perso.pv = self.pv.valeur
            self.perso.mana = self.mana.valeur

    def __repr__(self):
        return f"<{self.nom} {self.pv.valeur}/{self.pv.maximum}>"
