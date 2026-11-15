"""Sosie (Dishonored 2) : un double spectral combat à vos côtés et sert de leurre (4 tours)."""
from objet import Sort, ev


class Sosie(Sort):
    id = "sosie"
    nom = "Sosie"
    cout = 26
    cible = "soi"
    fx = "invocation"
    description = "Crée un double (50 % de vos PV) qui attaque et attire les coups ennemis (4 tours)."

    def executer(self, combat, acteur, cibles):
        r = combat.invoquer(acteur, "sosie")
        if r is None:
            return [ev("texte", texte="Trop d'alliés invoqués déjà !")]
        return [ev("anim", fx="invocation", acteur=acteur, cibles=[r]), ev("statut", cible=r, texte="Sosie", positif=True)]
