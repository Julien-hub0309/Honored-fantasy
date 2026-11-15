"""Pistolet : haut risque / haute récompense. S'il touche, le coup est TOUJOURS critique ; taux d'échec élevé."""


def resoudre(acteur, cible, rng):
    return rng.random() <= acteur.classe.toucher_pistolet(acteur.stat("DEX"), cible.stat("AGI"))
