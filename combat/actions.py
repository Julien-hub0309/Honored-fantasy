"""Exécuteurs d'actions de combat : attaquer, magie, défendre, fuir, utiliser (phase d'objet).

Les formules sont celles de la classe de l'acteur (classe/formules.py via ClasseDef).
Chaque exécuteur renvoie une liste d'événements (dicts) animés par combat/scene_combat.py.
"""
from objet import ev, epee, pistolet, grenade, potion_vie, potion_mana, queue_phenix, courage, reflexion
from objet.blink import Blink
from objet.attraction import Attriction
from objet.stop_time import StopTime
from objet.domino import Domino
from objet.courage import Courage
from objet.reflexion import Reflexion
from objet.vision_tenebres import VisionTenebres
from objet.possession import Possession
from objet.pli_temporel import PliTemporel
from objet.nuee_vorace import NueeVorace
from objet.rafale import Rafale
from objet.clignement_tueur import ClignementTueur
from objet.regard_vide import RegardVide
from objet.invocation_assassin import InvocationAssassin
from objet.attirance import Attirance
from objet.lien_arcanique import LienArcanique
from objet.longue_portee import LonguePortee
from objet.envoutement import Envoutement
from objet.marche_ombre import MarcheOmbre
from objet.sosie import Sosie

SORTS = {s.id: s for s in (Blink(), Attriction(), StopTime(), Domino(), Courage(), Reflexion(), VisionTenebres(), Possession(), PliTemporel(),
                           NueeVorace(), Rafale(), ClignementTueur(), RegardVide(), InvocationAssassin(), Attirance(), LienArcanique(),
                           LonguePortee(), Envoutement(), MarcheOmbre(), Sosie())}
ARMES_NOMS = {"melee": "Arme", "pistolet": "Pistolet", "grenade": "Grenade"}


# ------------------------------------------------------------------ Attaquer
def cout_arme(acteur, arme):
    return grenade.COUT_MANA if arme == "grenade" else 0


def peut(acteur, arme):
    return arme in acteur.classe.equipement and acteur.mana.valeur >= cout_arme(acteur, arme)


def attaquer(combat, acteur, arme, cible=None):
    """Arme de corps à corps / pistolet (critique garanti ou raté) / grenade (zone inévitable)."""
    rng = combat.rng
    cl = acteur.classe
    adv = combat.adversaires(acteur)
    if not adv:
        return []
    if arme == "grenade":
        acteur.mana.payer(grenade.COUT_MANA)
        e = [ev("annonce", texte=f"{acteur.nom} lance une Grenade !"), ev("anim", fx="explosion", acteur=acteur, cibles=list(adv))]
        for c in list(adv):                       # INÉVITABLE : aucun jet d'esquive
            e += combat.infliger(acteur, c, cl.degats_grenade(acteur.stat("INT"), c.stat("RES"), rng), nature="mag")
        return e
    if cible is None or not cible.vivant:
        cible = adv[0]
    if arme == "pistolet":
        e = [ev("annonce", texte=f"{acteur.nom} tire au pistolet"), ev("anim", fx="tir", acteur=acteur, cibles=[cible])]
        if pistolet.resoudre(acteur, cible, rng):
            e += combat.infliger(acteur, cible, cl.degats_pistolet(acteur.stat("FOR"), cible.stat("RES"), rng), crit=True)
        else:
            e.append(ev("rate", cible=cible))
        return e
    e = [ev("annonce", texte=f"{acteur.nom} attaque"), ev("anim", fx="coup", acteur=acteur, cibles=[cible])]
    touche, crit = epee.resoudre(acteur, cible, rng)
    if not touche:
        e.append(ev("rate", cible=cible))
    else:
        e += combat.infliger(acteur, cible, cl.degats_melee(acteur.arme_base, acteur.stat("FOR"), cible.stat("RES"), crit, rng), crit=crit)
    return e


# ------------------------------------------------------------------ Magie
def lancer(combat, acteur, sort_id, cibles=None):
    sort = SORTS[sort_id]
    cout = acteur.cout_sort(sort)
    if not acteur.mana.payer(cout):
        return [ev("texte", texte="Mana insuffisant !")]
    cibles = cibles or combat.cibles_par_defaut(acteur, sort)
    return [ev("annonce", texte=f"{acteur.nom} lance {sort.nom} !")] + sort.executer(combat, acteur, cibles)


# ------------------------------------------------------------------ Défendre
def defendre(combat, acteur):
    """Résistance +150 % (+200 % Garde Urbain) jusqu'au prochain tour du combattant."""
    acteur.en_defense = True
    pct = int((acteur.classe.mult_defense - 1) * 100)
    return [ev("annonce", texte=f"{acteur.nom} se met en garde"), ev("anim", fx="garde", acteur=acteur, cibles=[acteur]),
            ev("statut", cible=acteur, texte=f"RES +{pct}%", positif=True)]


# ------------------------------------------------------------------ Fuir
def fuir(combat, acteur):
    """Jet pondéré par l'Agilité du lanceur face à celle des ennemis."""
    if not combat.fuite_possible:
        return [ev("texte", texte="Impossible de fuir ce combat !")]
    adv = combat.adversaires(acteur)
    p = acteur.classe.probabilite_fuite(acteur.stat("AGI"), [a.stat("AGI") for a in adv])
    e = [ev("annonce", texte=f"{acteur.nom} tente de fuir...")]
    if combat.rng.random() < p:
        combat.etat = "fuite"
        e.append(ev("texte", texte="Le groupe s'échappe dans la brume !"))
    else:
        e.append(ev("texte", texte="La fuite échoue !"))
    return e


# ------------------------------------------------------------------ Phase d'objet
def utiliser(combat, acteur, objet, cible):
    e = [ev("annonce", texte=f"{acteur.nom} utilise {objet.nom}"), ev("anim", fx="soin", acteur=acteur, cibles=[cible])]
    eff = objet.effet
    if "revive" in eff:
        n = queue_phenix.reanimer(cible, eff["revive"])
        e.append(ev("soin", cible=cible, n=n, stat="PV") if n else ev("texte", texte=f"{cible.nom} n'a pas besoin d'être réanimé."))
        if n:
            e.append(ev("statut", cible=cible, texte="Réanimé !", positif=True))
    if "pv_pct" in eff and cible.vivant:
        e.append(ev("soin", cible=cible, n=potion_vie.soigner(cible, eff["pv_pct"]), stat="PV"))
    if "mana_pct" in eff:
        e.append(ev("soin", cible=cible, n=potion_mana.restaurer(cible, eff["mana_pct"]), stat="Mana"))
    if eff.get("buff") == "courage":
        courage.appliquer(cible); e.append(ev("statut", cible=cible, texte="FOR/RES +2", positif=True))
    if eff.get("buff") == "reflexion":
        reflexion.appliquer(cible); e.append(ev("statut", cible=cible, texte="INT/DEX +2", positif=True))
    acteur.objet_utilise = True
    combat.consommer(acteur, objet)
    return e
