"""Marche d'ombre (Dishonored 2) : forme furtive. Les ennemis ne vous voient plus 2 tours ; la prochaine frappe fait +50 %."""
from combat.rang import Alteration
from objet import Sort, ev


class MarcheOmbre(Sort):
    id = "marche_ombre"
    nom = "Marche d'ombre"
    cout = 14
    cible = "soi"
    fx = "buff"
    description = "Furtif 2 tours : non ciblable tant qu'un autre allié est visible ; prochaine frappe +50 %."

    def executer(self, combat, acteur, cibles):
        acteur.rang.ajouter(Alteration("furtif", "Furtif", 2))
        return [ev("anim", fx="buff", acteur=acteur, cibles=[acteur]), ev("statut", cible=acteur, texte="Furtif", positif=True)]
