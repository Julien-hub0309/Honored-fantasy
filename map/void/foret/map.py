"""Génération de la carte de Forêt Inversée (void/foret) : tracé procédural reproductible (graine) + contenu."""
import random

from map import moteur
from map.void.foret import elements, loot

BIOME = 'foret'
CLE = "void/foret"
PNJS = []


def creer(graine=0):
    rng = random.Random(f"{CLE}:{graine}")
    z = moteur.Zone('Forêt Inversée', 'void', BIOME, elements.PALETTE, 12, 64, 40)
    moteur.gen_nature(z, rng, densite=0.42, herbe=0.55, eau=0.02)
    return moteur.finaliser(z, rng, dict(cle=CLE, nb_coffres=4, boss=[4], verrou=[4], prosperite=1,
                                         ambiance=elements.AMBIANCE, musique='void', pnjs=PNJS))
