"""Génération de la carte de Catacombes du Guet (realme/donjon) : tracé procédural reproductible (graine) + contenu."""
import random

from map import moteur
from map.realme.donjon import elements, loot

BIOME = 'donjon'
CLE = "realme/donjon"
PNJS = [{'nom': 'Prisonnier hagard', 'sprite': 'pnj_civil', 'role': 'dialogue', 'slot': 'proche_entree', 'lignes': ["Prisonnier : Hargrave garde le couloir central. Et plus loin... l'Abbesse. Elle prie, mais pas pour nous."]}]


def creer(graine=0):
    rng = random.Random(f"{CLE}:{graine}")
    z = moteur.Zone('Catacombes du Guet', 'realme', BIOME, elements.PALETTE, 8, 58, 40)
    moteur.gen_donjon(z, rng, mid_boss=True)
    return moteur.finaliser(z, rng, dict(cle=CLE, nb_coffres=5, boss=[2, 3], verrou=[2, 3], prosperite=1,
                                         ambiance=elements.AMBIANCE, musique='donjon', pnjs=PNJS))
