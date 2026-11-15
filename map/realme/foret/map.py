"""Génération de la carte de Forêt de Grisvoile (realme/foret) : tracé procédural reproductible (graine) + contenu."""
import random

from map import moteur
from map.realme.foret import elements, loot

BIOME = 'foret'
CLE = "realme/foret"
PNJS = [{'nom': 'Vieux Bran', 'sprite': 'pnj_sage', 'role': 'dialogue', 'slot': 'proche_entree', 'lignes': ['Bran : Les hautes herbes grouillent de Monstres. Évitez-les si vous êtes blessés.', 'Bran : La Reine Ronce garde la sortie. Elle pare les coups mais craint les sorts qui ralentissent.']}]


def creer(graine=0):
    rng = random.Random(f"{CLE}:{graine}")
    z = moteur.Zone('Forêt de Grisvoile', 'realme', BIOME, elements.PALETTE, 3, 64, 40)
    moteur.gen_nature(z, rng, densite=0.46, herbe=0.55, eau=0.012)
    return moteur.finaliser(z, rng, dict(cle=CLE, nb_coffres=3, boss=[1], verrou=[1], prosperite=1,
                                         ambiance=elements.AMBIANCE, musique='foret', pnjs=PNJS))
