"""Revente : le joueur vend ses objets au marchand à 80 % de leur valeur d'achat (décote fixe de -20 %)."""
TAUX_REVENTE = 0.80


class Revente:
    def __init__(self, prix_achat):
        self.prix_achat = prix_achat

    def calculer_prix_revente(self):
        return int(self.prix_achat * TAUX_REVENTE)


def prix_revente(objet):
    """Les Runes Interdites et objets sans valeur ne se vendent pas."""
    if objet.type == "rune":
        return 0
    return Revente(objet.valeur).calculer_prix_revente()
