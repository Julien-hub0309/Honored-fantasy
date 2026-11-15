"""Bestiaire : fabrique d'ennemis (Combattant + IA) selon la classe, variantes de Monstres (cahier §4)."""
import classe as registre
from bot import ia_agressive_melee, ia_protector_defensive, ia_ranged_skirmisher, ia_support_healer
from combat.combattant import Combattant
from exploration.objets import depuis_id

IA_PAR_CLASSE = {"garde_urbain": ia_protector_defensive, "officier": ia_ranged_skirmisher, "sorciere": ia_ranged_skirmisher,
                 "harponneur": ia_ranged_skirmisher, "moine": ia_support_healer, "monstre": ia_agressive_melee}
NOMS = {"garde_urbain": "Garde Urbain", "officier": "Officier", "sorciere": "Sorcière", "moine": "Moine", "harponneur": "Harponneur", "monstre": "Monstre"}

# Les ennemis n'utilisent que le kit d'origine (les pouvoirs avancés de l'Outsider sont réservés aux héros)
KIT_ENNEMI = {"sorciere": ["blink", "attriction", "reflexion"], "harponneur": ["stop_time", "domino", "reflexion"]}

# Variantes de Monstres : modificateurs de stats, indice de sprite, poids de tirage
VARIANTES = [
    dict(nom="Rôdeur de brume", mods=dict(PV=1.0, FOR=0, RES=0, INT=0, DEX=0, AGI=0), variante=0, poids=40),
    dict(nom="Hurleur", mods=dict(PV=0.8, FOR=-1, RES=-1, INT=1, DEX=2, AGI=2), variante=1, poids=25),
    dict(nom="Écorcheur", mods=dict(PV=0.9, FOR=2, RES=-1, INT=0, DEX=1, AGI=0), variante=2, poids=20),
    dict(nom="Brute des marais", mods=dict(PV=1.35, FOR=1, RES=2, INT=-1, DEX=-1, AGI=-1), variante=3, poids=15),
]


def appliquer_variante(stats, rng, variante=None, void=False):
    t = VARIANTES[variante] if variante is not None else rng.choices(VARIANTES, [x["poids"] for x in VARIANTES])[0]
    s = dict(stats)
    s["PV"] = int(s["PV"] * t["mods"]["PV"])
    for k in ("FOR", "RES", "INT", "DEX", "AGI"):
        s[k] = max(1, s[k] + t["mods"][k])
    return s, ("Fragment de " if void else "") + t["nom"], t["variante"]


def equiper_ennemi(ennemi, rng, boss=False):
    """Inventaire ennemi : consommables portés (phase d'objet de l'IA)."""
    if boss:
        ennemi.inventaire = [depuis_id("potion_vie"), depuis_id("potion_vie")]
    elif ennemi.classe.id in ("officier", "moine") and rng.random() < 0.35:
        ennemi.inventaire = [depuis_id("potion_vie")]


def creer_ennemi(classe_id, niveau, rng, void=False, variante=None):
    cl = registre.obtenir(classe_id)
    stats = cl.stats(niveau)
    nom, var = NOMS[classe_id], 0
    if classe_id == "monstre":
        stats, nom, var = appliquer_variante(stats, rng, variante, void)
    elif void:
        nom += " spectral"
    c = Combattant(nom, classe_id, niveau, stats, False, void=void, variante=var)
    c.ia = IA_PAR_CLASSE[classe_id].decider
    kit = KIT_ENNEMI.get(classe_id)
    if kit is not None:
        c.sorts = [s for s in c.sorts if s in kit]
    c.xp = int(9 + niveau * 5.5)
    c.gain_or = int(rng.randint(5, 10) + niveau * 3)
    c.arme_base = int(c.arme_base * 1.3)          # équilibrage : les ennemis frappent un peu plus fort que les héros
    equiper_ennemi(c, rng)
    return c
