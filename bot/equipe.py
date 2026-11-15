"""Compagnons : les 4 condamnés de départ (perso_1..4) + l'Officier déchu. Sélection de l'équipe (5 classes, 4 places)."""
PERSO_1 = dict(
    slot=1, nom="Aldous", classe="garde_urbain", titre="Ex-capitaine du Guet",
    crime="A refusé d'ouvrir le feu sur la foule du Quai des Veuves.",
    repliques=dict(victoire="Le Guet tient toujours.", ko="Je... tiens encore...", debut="En formation !"),
)

PERSO_2 = dict(
    slot=2, nom="Maëlys", classe="sorciere", titre="Apothicaire maudite",
    crime="Accusée d'avoir invoqué la peste du Void... ce qui est en partie vrai.",
    repliques=dict(victoire="Le Void approuve.", ko="L'Autre Monde m'appelle...", debut="Pas un geste, ou je vous efface."),
)

PERSO_3 = dict(
    slot=3, nom="Thaddée", classe="moine", titre="Surveillant défroqué",
    crime="Hérésie : il a douté publiquement de l'Abbaye.",
    repliques=dict(victoire="Que l'Outsider nous pardonne.", ko="Ma foi... vacille...", debut="Priez, il en est encore temps."),
)

PERSO_4 = dict(
    slot=4, nom="Ysolde", classe="harponneur", titre="Harponneuse mutine",
    crime="Mutinerie à bord du Léviathan Rouge.",
    repliques=dict(victoire="Une de plus pour la cale !", ko="Pas... encore...", debut="À l'eau, les rats !"),
)

from bot.etat import Personnage

OFFICIER = dict(
    slot=5, nom="Rennick", classe="officier", titre="Officier déchu",
    crime="A détourné la solde de sa garnison pour nourrir des orphelins.",
    repliques=dict(victoire="Conforme au plan.", ko="Repliez-vous...", debut="Exécution !"),
)
ROSTER = {p["classe"]: p for p in (PERSO_1, PERSO_2, PERSO_3, PERSO_4, OFFICIER)}
# Les quatre héros sont des animaux, respectivement : capybara, panda, renard, loup.
ESPECES_SLOTS = ["capybara", "panda", "renard", "loup"]
NOMS_SLOTS = ["Capy", "Bao", "Roux", "Fenris"]
DEFAUT = ["garde_urbain", "moine", "sorciere", "harponneur"]     # capybara tank, panda moine, renard sorcier, loup harponneur


NOMS_PAR_DEFAUT = {c: ROSTER[c]["nom"] for c in ROSTER}
LONGUEUR_NOM_MAX = 12


def creer_equipe(choix):
    """choix : liste de 4 éléments, soit un identifiant de classe, soit un couple (nom, classe).

    Les classes peuvent se répéter ; les noms identiques sont numérotés pour rester distincts en combat."""
    persos, vus = [], {}
    for i, c in enumerate(choix):
        nom, classe_id = c if isinstance(c, tuple) else (None, c)
        nom = (nom or "").strip()[:LONGUEUR_NOM_MAX] or NOMS_SLOTS[i]
        vus[nom] = vus.get(nom, 0) + 1
        if vus[nom] > 1:
            nom = f"{nom[:LONGUEUR_NOM_MAX - 2]} {vus[nom]}"
        p = Personnage(nom, classe_id, 1, i + 1)
        p.espece = ESPECES_SLOTS[i]
        persos.append(p)
    return persos


def adapter_dialogue(lignes, equipe):
    """Les répliques des boss nomment les compagnons d'origine ; on les remplace par les vrais noms du groupe.

    Si la classe du compagnon cité n'est pas dans le groupe, sa réplique est supprimée."""
    par_nom = {r["nom"]: c for c, r in ROSTER.items()}
    sortie = []
    for nom, txt in lignes:
        if nom in par_nom:
            membre = next((p for p in equipe if p.classe_id == par_nom[nom]), None)
            if membre is None:
                continue
            nom = membre.nom
        sortie.append((nom, txt))
    return sortie or list(lignes)


def replique(classe_id, cle):
    return ROSTER[classe_id]["repliques"][cle]
