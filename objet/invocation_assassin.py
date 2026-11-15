"""Invocation d'assassin (DLC Daud) : un assassin de l'ombre combat à vos côtés pendant 4 tours."""
from objet import Sort, ev


class InvocationAssassin(Sort):
    id = "invocation_assassin"
    nom = "Invocation d'assassin"
    cout = 28
    cible = "soi"
    fx = "invocation"
    description = "Invoque un assassin allié (4 tours, 2 invocations maximum en même temps)."

    def executer(self, combat, acteur, cibles):
        r = combat.invoquer(acteur, "assassin")
        if r is None:
            return [ev("texte", texte="Trop d'alliés invoqués déjà !")]
        return [ev("anim", fx="invocation", acteur=acteur, cibles=[r]), ev("statut", cible=r, texte="Assassin", positif=True)]
