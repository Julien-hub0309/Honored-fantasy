"""Les 6 Boss majeurs : Realme (Reine Ronce, Prévôt Hargrave, Abbesse Veyra) et Void (Kael, Maréchal Ossian, Lord Vaerith).

Chaque boss : fiche BOSS_n (stats, sorts, dialogues, rune lâchée) + fonction decider_n (IA à phases/rotation)
+ attaques signatures. creer_boss(n) instancie le Combattant.
"""
import classe as registre
from bot import degats as D
from bot.bestiaire import equiper_ennemi
from bot.cible import melee, pistolet, plus_agile, plus_faible, plus_dangereux, peut_sort
from combat import actions as act
from combat.combattant import Combattant
from combat.mana import Mana
from combat.rang import Alteration
from objet import ev

# --------------------------------------------------------------------------------------
# Boss 1 - Reine Ronce, souveraine de la Forêt de Grisvoile (Realme).
# --------------------------------------------------------------------------------------

BOSS_1 = dict(num=1, id="reine_ronce", nom="Reine Ronce", classe="sorciere", niveau=4, pv=560, mods=dict(FOR=0, RES=1, INT=5, DEX=1, AGI=2),
            sorts=["blink", "attriction"], sprite="reine_ronce", xp=170, or_=190, rune=0, rarete=(2, 3), echelle=3,
            intro=[("Reine Ronce", "Des condamnés... la forêt vous a sentis venir. Elle a faim."), ("Aldous", "Pas un pas de plus, sorcière.")],
            outro=[("Reine Ronce", "Prenez la Rune... Il vous attend... dans le Void..."), ("Maëlys", "Elle parlait de lui. L'Antagoniste.")])


def _entraver_1(c):
    c.rang.ajouter(Alteration("entrave", "Entravé", 2, fixe={"AGI": 0}, positif=False))
    return [ev("statut", cible=c, texte="Entravé", positif=False)]


def etreinte_1(combat, a):
    return D.zone(combat, a, "Étreinte des ronces", 12, 1.0, "attriction", "mag", 2.2, extra=_entraver_1)


def seve_1(combat, a):
    return D.soin(a, 0.12, "Sève vitale")


def decider_1(combat, a):
    t = D.tour(a)
    adv = combat.adversaires(a)
    if a.pv.ratio < 0.45 and t % 5 == 0:
        return None, {"type": "special", "fn": seve_1}
    if t % 3 == 0:
        return None, {"type": "special", "fn": etreinte_1}
    if t % 2 == 0 and peut_sort(combat, a, "attriction"):
        return None, {"type": "magie", "sort": "attriction", "cibles": [plus_agile(adv)]}
    if peut_sort(combat, a, "blink"):
        return None, {"type": "magie", "sort": "blink", "cibles": [plus_faible(adv)]}
    return None, melee(plus_faible(adv))

# --------------------------------------------------------------------------------------
# Boss 2 - Haut-Prévôt Hargrave, geôlier des Catacombes (Realme).
# --------------------------------------------------------------------------------------

BOSS_2 = dict(num=2, id="prevot", nom="Prévôt Hargrave", classe="garde_urbain", niveau=7, pv=800, mods=dict(FOR=3, RES=1, INT=0, DEX=2, AGI=0),
            sorts=["courage"], sprite="prevot", xp=260, or_=300, rune=1, rarete=(3, 4), echelle=3,
            intro=[("Hargrave", "Le Guet n'a pas de pitié pour les évadés."), ("Ysolde", "Gros bonhomme, gros tonneau... ça s'enfonce bien.")],
            outro=[("Hargrave", "L'ordre... s'effondre..."), ("Thaddée", "Un pilier de moins. Mais l'Abbaye nous attend.")])


def salve_2(combat, a):
    e = [ev("annonce", texte="Hargrave : Salve du Guet !"), ev("anim", fx="tir", acteur=a, cibles=combat.adversaires(a))]
    for c in list(combat.adversaires(a)):
        if combat.rng.random() < 0.75:
            e += combat.infliger(a, c, int(D.puissance(a, 8, 0, 3.2, 1.0, combat.rng) * (1 - 0.5 * c.stat("RES") / (c.stat("RES") + 12))), "phys", True)
        else:
            e.append(ev("rate", cible=c))
    return e


def decider_2(combat, a):
    t = D.tour(a)
    adv = combat.adversaires(a)
    if a.pv.ratio < 0.5 and not a.cd.get("rage") and peut_sort(combat, a, "courage"):
        a.cd["rage"] = 99
        return None, {"type": "magie", "sort": "courage", "cibles": [a]}
    if t % 4 == 0:
        return None, {"type": "defendre"}
    if t % 3 == 0:
        return None, {"type": "special", "fn": salve_2}
    if t % 2 == 0:
        return None, pistolet(plus_faible(adv))
    return None, melee(plus_dangereux(adv))

# --------------------------------------------------------------------------------------
# Boss 3 - Abbesse Veyra, Haute Surveillante de l'Abbaye (Realme).
# --------------------------------------------------------------------------------------

BOSS_3 = dict(num=3, id="abbesse", nom="Abbesse Veyra", classe="moine", niveau=10, pv=780, mods=dict(FOR=2, RES=-2, INT=4, DEX=2, AGI=2),
            sorts=["courage", "reflexion"], sprite="abbesse", xp=380, or_=420, rune=2, rarete=(3, 4), echelle=3,
            intro=[("Veyra", "L'Outsider est une hérésie. Vous êtes ses marionnettes."), ("Thaddée", "Veyra... vous m'avez appris à prier.")],
            outro=[("Veyra", "La faille... elle s'ouvre... Pendysia est perdue."), ("Aldous", "Alors nous irons la refermer. De l'autre côté.")])


def jugement_3(combat, a):
    cible = max(combat.adversaires(a), key=lambda c: c.pv.valeur)
    return D.cible_unique(combat, a, cible, "Jugement", 28, 1.4, "blink", "mag", 3.2)


def cantique_3(combat, a):
    from objet.courage import appliquer
    appliquer(a)
    return D.soin(a, 0.05, "Cantique de grâce")


def decider_3(combat, a):
    t = D.tour(a)
    adv = combat.adversaires(a)
    if t % 5 == 0 or (a.pv.ratio < 0.35 and t % 4 == 0):
        return None, {"type": "special", "fn": cantique_3}
    if t % 3 == 0 and act.peut(a, "grenade"):
        return None, {"type": "attaquer", "arme": "grenade"}
    if t % 2 == 0:
        return None, {"type": "special", "fn": jugement_3}
    return None, melee(plus_faible(adv))

# --------------------------------------------------------------------------------------
# Boss 4 - Chasseur d'âmes Kael, Harponneur du Void.
# --------------------------------------------------------------------------------------

BOSS_4 = dict(num=4, id="kael", nom="Kael le Chasseur", classe="harponneur", niveau=13, pv=1250, mods=dict(FOR=1, RES=-1, INT=0, DEX=2, AGI=2),
            sorts=["stop_time", "domino", "attriction"], sprite="kael", xp=520, or_=560, rune=3, rarete=(3, 5), echelle=3,
            intro=[("Kael", "Dans le Void, les baleines sont des âmes. Et vous êtes à l'hameçon."), ("Ysolde", "Kael ! Tu étais mon second !")],
            outro=[("Kael", "Il... ne pardonne pas... les échecs..."), ("Ysolde", "Va en paix, vieux loup.")])


def harpon_ame_4(combat, a):
    return D.cible_unique(combat, a, plus_dangereux(combat.adversaires(a)), "Harpon d'âme", 30, 1.5, "tir", "phys", 0, 4.4, crit=True)


def decider_4(combat, a):
    t = D.tour(a)
    adv = combat.adversaires(a)
    if combat.temps_fige and combat.temps_fige["lanceur"] is a:
        return None, {"type": "special", "fn": harpon_ame_4}
    if not a.cd.get("stop_time") and peut_sort(combat, a, "stop_time") and t % 4 == 1:
        a.cd["stop_time"] = 6
        return None, {"type": "magie", "sort": "stop_time"}
    if not a.cd.get("domino") and len(adv) >= 2 and peut_sort(combat, a, "domino") and not any(c.lien for c in adv):
        a.cd["domino"] = 5
        return None, {"type": "magie", "sort": "domino", "cibles": sorted(adv, key=lambda c: -c.pv.valeur)[:2]}
    if t % 2 == 0:
        return None, {"type": "special", "fn": harpon_ame_4}
    return None, melee(plus_faible(adv))

# --------------------------------------------------------------------------------------
# Boss 5 - Maréchal Ossian, spectre de la Garnison du Void.
# --------------------------------------------------------------------------------------

BOSS_5 = dict(num=5, id="ossian", nom="Maréchal Ossian", classe="officier", niveau=15, pv=1250, mods=dict(FOR=0, RES=-1, INT=1, DEX=2, AGI=2),
            sorts=["reflexion", "courage"], sprite="ossian", xp=640, or_=700, rune=4, rarete=(4, 5), echelle=3,
            intro=[("Ossian", "Garnison, au rapport. Des intrus dans la Cathédrale."), ("Rennick", "Maréchal... J'ai servi sous vos ordres.")],
            outro=[("Ossian", "Pour... la Couronne du Void..."), ("Aldous", "Plus qu'un. Le dernier.")])


def barrage_5(combat, a):
    return D.zone(combat, a, "Barrage spectral", 22, 1.0, "explosion", "mag", 2.6)


def decider_5(combat, a):
    t = D.tour(a)
    adv = combat.adversaires(a)
    if t == 1 and peut_sort(combat, a, "reflexion"):
        return None, {"type": "magie", "sort": "reflexion", "cibles": [a]}
    if t % 3 == 0:
        return None, {"type": "special", "fn": barrage_5}
    if t % 2 == 0 and act.peut(a, "grenade"):
        return None, {"type": "attaquer", "arme": "grenade"}
    if combat.rng.random() < 0.4:
        return None, pistolet(plus_faible(adv))
    return None, melee(plus_faible(adv))

# --------------------------------------------------------------------------------------
# Boss 6 - Lord Vaerith, l'Antagoniste : ancien porteur de la Marque de l'Outsider, usurpateur du Void.
# --------------------------------------------------------------------------------------

BOSS_6 = dict(num=6, id="vaerith", nom="Lord Vaerith", classe="sorciere", niveau=18, pv=1950, mods=dict(FOR=0, RES=-1, INT=-2, DEX=3, AGI=3),
            sorts=["blink", "attriction", "domino", "stop_time", "courage"], sprite="vaerith", xp=1500, or_=2000, rune=5, rarete=(5, 5), echelle=4,
            intro=[("Vaerith", "Les Runes Interdites... Vous les avez toutes. Comme c'est commode."),
                   ("Aldous", "Votre règne s'arrête ici, Vaerith."),
                   ("Vaerith", "Je prendrai la place de l'Outsider. Et vous serez mon premier miracle.")],
            outro=[("Vaerith", "Impossible... Le Void... me rejette..."), ("Maëlys", "Il est temps de sceller la faille.")])


def marque_6(combat, a):
    e = D.zone(combat, a, "Marque de l'Outsider", 18, 1.0, "temps", "mag", 2.0)
    e += D.soin(a, 0.02, "Il se nourrit de la Marque")[1:]
    return e


def decider_6(combat, a):
    t = D.tour(a)
    adv = combat.adversaires(a)
    r = a.pv.ratio
    a.phase_boss = 1 if r > 0.66 else (2 if r > 0.33 else 3)
    if a.phase_boss == 3 and t % 2 == 0:
        return None, {"type": "special", "fn": marque_6}
    if a.phase_boss >= 2 and not a.cd.get("stop_time") and peut_sort(combat, a, "stop_time") and not combat.temps_fige:
        a.cd["stop_time"] = 8
        return None, {"type": "magie", "sort": "stop_time"}
    if combat.temps_fige and combat.temps_fige["lanceur"] is a:
        return None, {"type": "special", "fn": marque_6} if a.phase_boss >= 2 else {"type": "magie", "sort": "blink", "cibles": [plus_faible(adv)]}
    if not a.cd.get("domino") and len(adv) >= 2 and peut_sort(combat, a, "domino") and not any(c.lien for c in adv):
        a.cd["domino"] = 5
        return None, {"type": "magie", "sort": "domino", "cibles": sorted(adv, key=lambda c: -c.pv.valeur)[:2]}
    if a.phase_boss >= 2 and not a.rang.a("courage") and peut_sort(combat, a, "courage") and t % 4 == 0:
        return None, {"type": "magie", "sort": "courage", "cibles": [a]}
    if t % 3 == 0 and peut_sort(combat, a, "attriction"):
        return None, {"type": "magie", "sort": "attriction", "cibles": [plus_agile(adv)]}
    if peut_sort(combat, a, "blink"):
        return None, {"type": "magie", "sort": "blink", "cibles": [plus_faible(adv)]}
    return None, melee(plus_faible(adv))


BOSS_PAR_NUM = {n: (globals()[f"BOSS_{n}"], globals()[f"decider_{n}"]) for n in range(1, 7)}


def infos(num):
    return BOSS_PAR_NUM[num][0]


def creer_boss(num, rng):
    d, decider = BOSS_PAR_NUM[num]
    cl = registre.obtenir(d["classe"])
    stats = cl.stats(d["niveau"])
    stats["PV"] = d["pv"]
    stats["Mana"] = max(stats["Mana"], 160)
    for k, v in d["mods"].items():
        stats[k] += v
    c = Combattant(d["nom"], d["classe"], d["niveau"], stats, False, sorts=d["sorts"], boss=True, sprite=d["sprite"], void=num >= 4)
    c.ia = decider
    c.xp, c.gain_or = d["xp"], d["or_"]
    c.arme_base = cl.arme["degats_base"] + 4 * num
    equiper_ennemi(c, rng, boss=True)
    return c
