"""Queue de Phénix : réanime un allié KO."""
POURCENTAGES = {"queue_phenix": 0.5}


def reanimer(cible, pourcentage):
    """Rend des PV à un combattant KO. Retourne les PV rendus (0 si la cible n'était pas KO)."""
    if cible.vivant:
        return 0
    n = cible.pv.gagner(max(1, int(cible.pv.maximum * pourcentage)))
    cible.alpha = 255
    cible.en_defense = False
    return n
