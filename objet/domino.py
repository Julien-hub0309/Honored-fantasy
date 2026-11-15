"""Domino : lie deux ennemis 3 tours. Les dégâts de l'un sont répliqués sur l'autre ; si l'un meurt, l'autre aussi."""
from objet import Sort, ev


class Domino(Sort):
    id = "domino"
    nom = "Domino"
    cout = 22
    cible = "deux_ennemis"
    fx = "domino"
    description = "Lie deux cibles 3 tours : dégâts partagés, la mort de l'une entraîne l'autre."

    def executer(self, combat, acteur, cibles):
        a, b = cibles[0], cibles[1]
        for x, y in ((a, b), (b, a)):
            x.lien, x.lien_duree = y, 3
        return [ev("anim", fx="domino", acteur=acteur, cibles=[a, b]),
                ev("statut", cible=a, texte="Domino", positif=False), ev("statut", cible=b, texte="Domino", positif=False)]
