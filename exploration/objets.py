"""Catalogue d'objets : consommables, armes de corps à corps par classe, talismans, Runes Interdites.

6 niveaux de rareté (cahier des charges §5.2) : Commun, Peu commun, Rare | Très rare, Épique, Légendaire.
"""
import copy
from dataclasses import dataclass, field

from assets import pixelart as px

RARETES = px.RARETE_NOMS
ARMES_NOMS = {
    "garde_urbain": ["Lame du Guet", "Sabre de ronde", "Espadon de garnison", "Fendoir des Remparts", "Gardienne d'Acier-Noir", "Éclat du Premier Rempart"],
    "officier": ["Sabre d'apparat", "Rapière de parade", "Sabre d'abordage", "Lame de commandement", "Rapière d'Argent-Vif", "Éclair du Capitaine"],
    "sorciere": ["Dague rituelle", "Kriss d'os", "Stylet d'obsidienne", "Serpe de lune", "Faucille du Crépuscule", "Croc de l'Outsider"],
    "moine": ["Bâton bénit", "Maillet de prière", "Masse de l'Abbaye", "Crosse de fer", "Sceptre de Contrition", "Verge du Jugement"],
    "harponneur": ["Harpon vicieux", "Harpon de cale", "Foëne barbelée", "Harpon à huile", "Foëne du Léviathan", "Lance du Grand Cachalot"],
}
ARME_BONUS = [0, 3, 6, 10, 15, 21]
TALISMANS = {"FOR": "Croc de baleine", "RES": "Médaillon du Guet", "INT": "Fiole d'huile pure", "DEX": "Œil de verre",
             "AGI": "Plume de corbeau", "PV": "Cœur de pierre", "Mana": "Éclat du Void"}
ADJ = ["terni", "poli", "ouvragé", "sanctifié", "d'exception", "de l'Outsider"]
PRIX_RARETE = [1, 2.6, 6, 14, 32, 70]


@dataclass
class Objet:
    id: str
    nom: str
    type: str                  # conso | arme | talisman | rune
    rarete: int = 0
    valeur: int = 10           # valeur d'achat (la revente rapporte 80 % de cette valeur)
    effet: dict = field(default_factory=dict)
    classe: str = None         # restriction de classe (armes)
    degats_base: int = 0
    bonus: dict = field(default_factory=dict)
    desc: str = ""

    @property
    def icone(self):
        c = px.RARETE_COULEURS[self.rarete]
        if self.type == "arme":
            return px.icone("epee", c, self.rarete)
        if self.type == "talisman":
            return px.icone("talisman", c, self.rarete)
        if self.type == "rune":
            return px.icone("rune", (200, 100, 255), 5)
        if "revive" in self.effet:
            return px.icone("plume", (255, 130, 40), self.rarete)
        coul = {"potion_vie": (230, 70, 80), "potion_mana": (80, 130, 255), "elixir": (240, 190, 70)}
        k = "potion_vie" if "pv_pct" in self.effet else ("potion_mana" if "mana_pct" in self.effet else "elixir")
        return px.icone("potion", coul[k], self.rarete)

    def copie(self, valeur=None):
        o = copy.copy(self)
        o.effet, o.bonus = dict(self.effet), dict(self.bonus)
        if valeur is not None:
            o.valeur = valeur
        return o


CONSOS = {
    "potion_vie": Objet("potion_vie", "Potion de Vie", "conso", 0, 30, {"pv_pct": 0.5}, desc="Restaure 50 % des PV max."),
    "potion_vie_plus": Objet("potion_vie_plus", "Potion de Vie+", "conso", 2, 90, {"pv_pct": 1.0}, desc="Restaure 100 % des PV max."),
    "potion_mana": Objet("potion_mana", "Potion de Mana", "conso", 0, 35, {"mana_pct": 0.5}, desc="Restaure 50 % du Mana max."),
    "potion_mana_plus": Objet("potion_mana_plus", "Potion de Mana+", "conso", 2, 100, {"mana_pct": 1.0}, desc="Restaure 100 % du Mana max."),
    "elixir_courage": Objet("elixir_courage", "Élixir de Courage", "conso", 1, 55, {"buff": "courage"}, desc="FOR et RES +2 pendant 3 tours."),
    "queue_phenix": Objet("queue_phenix", "Queue de Phénix", "conso", 3, 260, {"revive": 0.5}, desc="Réanime un allié KO avec 50 % de ses PV."),
    "elixir_reflexion": Objet("elixir_reflexion", "Élixir de Réflexion", "conso", 1, 55, {"buff": "reflexion"}, desc="INT et DEX +2 pendant 3 tours."),
}
RUNES = ["Rune de la Ronce", "Rune du Prévôt", "Rune de l'Abbesse", "Rune du Harponneur", "Rune du Spectre", "Rune de l'Usurpateur"]


def fabriquer_arme(classe_id, rarete):
    from classe import obtenir
    base = obtenir(classe_id).arme["degats_base"]
    d = base + ARME_BONUS[rarete] if rarete else base
    nom = ARMES_NOMS[classe_id][rarete]
    return Objet(f"arme:{classe_id}:{rarete}", nom, "arme", rarete, int(25 * PRIX_RARETE[rarete]), classe=classe_id,
                 degats_base=d, desc=f"Dégâts de base {d}.")


def fabriquer_talisman(stat, rarete):
    n = 1 + (rarete + 1) // 2
    bonus = {stat: n} if stat not in ("PV", "Mana") else {stat: (12 if stat == "PV" else 8) * (rarete + 1)}
    if rarete >= 4 and stat not in ("PV", "Mana"):
        bonus["PV"] = 10 * rarete
    return Objet(f"tali:{stat}:{rarete}", f"{TALISMANS[stat]} {ADJ[rarete]}", "talisman", rarete, int(30 * PRIX_RARETE[rarete]),
                 bonus=bonus, desc=", ".join(f"{k} +{v}" for k, v in bonus.items()))


def fabriquer_rune(i):
    return Objet(f"rune:{i}", RUNES[i], "rune", 5, 0, desc="Rune Interdite arrachée à un Gardien du Void.")


def depuis_id(id_, valeur=None):
    """Reconstruit un objet depuis son identifiant (sauvegarde)."""
    if id_ in CONSOS:
        o = CONSOS[id_].copie()
    elif id_.startswith("arme:"):
        _, c, r = id_.split(":"); o = fabriquer_arme(c, int(r))
    elif id_.startswith("tali:"):
        _, s, r = id_.split(":"); o = fabriquer_talisman(s, int(r))
    elif id_.startswith("rune:"):
        o = fabriquer_rune(int(id_.split(":")[1]))
    else:
        raise KeyError(id_)
    if valeur is not None:
        o.valeur = valeur
    return o


def groupes(sac):
    """Regroupe les objets identiques (même id) pour l'affichage : [(objet, quantité)]."""
    vus, res = {}, []
    for o in sac:
        if o.id in vus:
            res[vus[o.id]][1] += 1
        else:
            vus[o.id] = len(res)
            res.append([o, 1])
    return [(o, n) for o, n in res]


# --------------------------------------------------------------------------------------
# Sac à dos du groupe (et contenu des coffres)
# --------------------------------------------------------------------------------------
class Inventaire:
    def __init__(self):
        self.objets = []

    def ajouter(self, o):
        self.objets.append(o)

    def retirer(self, o):
        for i, x in enumerate(self.objets):
            if x is o:
                self.objets.pop(i)
                return True
        return False

    def conso(self):
        return [o for o in self.objets if o.type == "conso"]

    def equipements(self, type_, classe=None):
        return [o for o in self.objets if o.type == type_ and (classe is None or o.classe in (None, classe))]

    def groupes(self, filtre=None):
        return groupes([o for o in self.objets if filtre is None or filtre(o)])

    def vers_dict(self):
        return [[o.id, o.valeur] for o in self.objets]

    @classmethod
    def depuis_dict(cls, data):
        inv = cls()
        for id_, val in data:
            inv.objets.append(depuis_id(id_, val))
        return inv
