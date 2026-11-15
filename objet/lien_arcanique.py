"""Lien arcanique (DLC Daud) : partage vos passifs avec les alliés pendant 4 tours."""
from combat.rang import Alteration
from objet import Sort, ev


class LienArcanique(Sort):
    id = "lien_arcanique"
    nom = "Lien arcanique"
    cout = 20
    cible = "allies"
    fx = "buff"
    description = "Partage vos passifs (Agilité, Vitalité, Soif de sang, Meurtrier de l'ombre) au groupe 4 tours."

    def executer(self, combat, acteur, cibles):
        e = [ev("anim", fx="buff", acteur=acteur, cibles=cibles)]
        passifs = set(acteur.passifs)
        for c in cibles:
            if c is acteur:
                continue
            ajout = {"AGI": 2 if "agilite" in passifs else 1}
            c.rang.ajouter(Alteration("lien_arcanique", "Lien arcanique", 4, ajout=ajout))
            for p in passifs:
                c.rang.ajouter(Alteration("lien_" + p, "Lien : " + p, 4))
            if "vitalite" in passifs:
                n = c.pv.gagner(int(c.pv.maximum * 0.15))
                if n:
                    e.append(ev("soin", cible=c, n=n, stat="PV"))
            e.append(ev("statut", cible=c, texte="Lien arcanique", positif=True))
        return e
