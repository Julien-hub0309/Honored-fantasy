"""Pouvoirs de l'Outsider utilisables hors combat (touche P) : bonds, vision à travers les murs, détection des Runes,
attraction des objets, furtivité. Le coût en mana est payé par un membre du groupe qui connaît le pouvoir."""
from map import moteur as M

VECTEURS = {"haut": (0, -1), "bas": (0, 1), "gauche": (-1, 0), "droite": (1, 0)}
INFOS = {
    "blink": dict(nom="Clignement", cout=6, desc="Téléportation courte : jusqu'à 4 cases devant vous, même derrière un mur."),
    "longue_portee": dict(nom="Longue portée", cout=8, desc="Grappin d'ombre : bond jusqu'à 8 cases devant vous."),
    "vision_tenebres": dict(nom="Vision des ténèbres", cout=8, desc="Voir à travers les murs : PNJ, coffres, objets, Gardiens (15 s)."),
    "regard_vide": dict(nom="Regard du Vide", cout=10, desc="Détecte les Runes (Gardiens) et les coffres, avec une boussole (20 s)."),
    "attraction": dict(nom="Attraction", cout=12, desc="Attire à vous tous les objets à moins de 8 cases."),
    "marche_ombre": dict(nom="Marche d'ombre", cout=8, desc="Forme furtive : rencontres très rares pendant 60 pas."),
}


def disponibles(etat):
    """[(id, infos, membre)] : pour chaque pouvoir, le membre vivant qui le connaît et qui a le plus de mana."""
    res = []
    for pid, info in INFOS.items():
        connus = [p for p in etat.equipe if p.vivant and pid in p.sorts()]
        if connus:
            res.append((pid, info, max(connus, key=lambda p: p.mana)))
    return res


def _saut(scene, portee):
    dx, dy = VECTEURS[scene.dir]
    arrivee = None
    for d in range(1, portee + 1):
        x, y = scene.x + dx * d, scene.y + dy * d
        t = scene.zone.tuile(x, y)
        if t in M.SOLIDES or t in (M.SORTIE_PREV, M.SORTIE_NEXT) or scene.entite_en(x, y):
            continue
        if not (0 < x < scene.zone.w - 1 and 0 < y < scene.zone.h - 1):
            continue
        arrivee = (x, y)
    if arrivee is None:
        return False, "Aucun point d'arrivée dans cette direction."
    scene.teleporter(arrivee)
    return True, ""


def utiliser(scene, pid, membre):
    """Retourne (succès, message). Le mana n'est dépensé qu'en cas de succès."""
    info = INFOS[pid]
    if membre.mana < info["cout"]:
        return False, f"{membre.nom} n'a pas assez de mana."
    if pid == "blink":
        ok, msg = _saut(scene, 4)
    elif pid == "longue_portee":
        ok, msg = _saut(scene, 8)
    elif pid == "vision_tenebres":
        scene.vision, scene.regard, ok, msg = 15.0, 0.0, True, ""
    elif pid == "regard_vide":
        scene.regard, scene.vision, ok, msg = 20.0, 0.0, True, ""
    elif pid == "marche_ombre":
        scene.furtif_pas, ok, msg = 60, True, ""
    elif pid == "attraction":
        proches = [s for s in scene.sol if abs(s["x"] - scene.x) + abs(s["y"] - scene.y) <= 8]
        if not proches:
            return False, "Aucun objet à portée."
        for s in proches:
            scene.sol.remove(s)
            scene.jeu.etat.sac.ajouter(s["objet"])
            scene.jeu.notif.ajouter(f"Attiré : {s['objet'].nom}", scene.jeu.notif_couleur(s["objet"].rarete), 2.0)
        ok, msg = True, ""
    if ok:
        membre.mana -= info["cout"]
        scene.jeu.audio.jouer("blink" if "portee" in pid or pid == "blink" else "magie")
    return ok, msg
